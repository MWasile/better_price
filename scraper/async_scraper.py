import asyncio
import dataclasses
import decimal
import difflib
import sys

import aiohttp
import bs4

from dataclasses import asdict
from dataclasses import dataclass
from decimal import Decimal

from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from config import settings
from scraper import models, tasks, signals


class ScrapEngine:
    MATCH_SETTINGS = 0.75

    async def scrap_request(self, session, task):
        timeout = aiohttp.ClientTimeout(total=60)
        proxy = settings.PROXY_URL

        async with session.get(task.url, timeout=timeout, proxy=proxy) as response:
            html = await response.text()

            data = await self.prettify_response(html, task)

            if task.email and data['price']:
                if await task.email_price_checker(data['price']):
                    await self.send_async_signal(task, data)
            if data:
                # TODO: don't save if data is incomplete
                await task.self_save(data)

    async def is_match(self, arg1, arg2):
        if not difflib.SequenceMatcher(None, arg1, arg2).ratio() > self.MATCH_SETTINGS:
            return False
        return True

    @staticmethod
    def send_signal(task, data):
        signals.email_success.send(
            sender='aioHttp',
            scrap_data={
                'id': task.owner_model_id,
                'task_info': data,
            })
        return True

    async def send_async_signal(self, task, data):
        return await asyncio.to_thread(self.send_signal, task, data)

    async def prettify_response(self, data_to_prettify, task):
        def p_text(qs):
            if qs is None:
                return None

            return qs.get_text(strip=True)

        def p_decimal(qs):
            if qs is None:
                return None

            pretty_price = qs.find(text=True, recursive=False).getText(strip=True)
            if pretty_price.find(',') != -1:
                pretty_price = pretty_price.replace(',', '.')

            pretty_price = "".join(char for char in pretty_price if char.isdigit() or char == '.')
            return pretty_price

        def p_attr(qs, attr):
            if qs is None:
                return None
            try:
                qsa = qs[attr]
                if not qsa.startswith('/'):
                    # TODO: support relative links.
                    return qsa
                return None
            except TypeError:
                return None

        tag_soup = bs4.BeautifulSoup(data_to_prettify, 'lxml')

        ebooks_in_container = tag_soup.select_one(task.querry_selectors['ALL_EBOOK_CONTAINER']). \
            select(task.querry_selectors['EBOOK_CONTAINER'])

        scrap_result = {}

        for ebook in ebooks_in_container:
            title = p_text(ebook.select_one(task.querry_selectors['EBOOK_DETAILS']['title']['qs']))

            if title and await self.is_match(title, task.user_input):

                for key, detail in task.querry_selectors['EBOOK_DETAILS'].items():
                    match detail['type']:
                        case 'text':
                            value = p_text(ebook.select_one(detail['qs']))
                        case 'decimal':
                            value = p_decimal(ebook.select_one(detail['qs']))
                        case 'attribute':
                            value = p_attr(ebook.select_one(detail['qs']), detail['attr'])
                        case _:
                            value = ""

                    scrap_result.update({key: value})
                return scrap_result
        return False

    async def setup_task(self, ready_tasks):
        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks_to_run = (self.scrap_request(session, task) for task in ready_tasks)
            await asyncio.gather(*tasks_to_run, return_exceptions=True)
            await session.close()


@dataclass
class Task:
    owner_model_id: int
    user_input: str
    _: dataclasses.KW_ONLY
    data: dict = None
    url: str = None
    bookstore_name: str = None
    querry_selectors: dict = None
    email: bool = None
    email_price: Decimal = None

    def __post_init__(self):
        # In celery, this class is initiated without any inheritance, but in Task Manager he needs to be mixed with
        # any bookstore class. If mixed, we need to grab necessary class attribute as url or queryselectors because
        # we are using 'asdict' when passing this class as args to Celery Worker.
        if self.__class__.__base__ != object:
            super().__init__(self.user_input)
            self.url = self.bookstores_url
            self.bookstore_name = self.__class__.__bases__[1].__qualname__
            self.querry_selectors = {
                'BOOKSTORE_URL': self.bookstores_url,
                'ALL_EBOOK_CONTAINER': self.ALL_EBOOK_CONTAINER,
                'EBOOK_CONTAINER': self.EBOOK_CONTAINER,
                'EBOOK_DETAILS': self.EBOOK_DETAILS
            }

    async def self_save(self, data_from_bookstores):
        @sync_to_async
        def wrapper():
            ct = ContentType.objects.get(app_label='scraper', model='fasttaskinfo')
            new_model = models.ScrapEbookResult(
                content_type=ct,
                object_id=self.owner_model_id,
                web_bookstore=self.bookstore_name,
                web_author=data_from_bookstores['author'],
                web_title=data_from_bookstores['title'],
                web_price=data_from_bookstores['price'],
                web_url=data_from_bookstores['url'],
                web_image_url=data_from_bookstores['jpg']
            )

            # new_model.save()
            try:
                new_model.full_clean()
                new_model.save()
            except ValidationError:
                return None

        await wrapper()

    async def email_price_checker(self, price_from_website):
        try:
            if Decimal(price_from_website) <= Decimal(self.email_price):
                return True
            return False
        except decimal.InvalidOperation:
            return False


class TaskManager:
    def __init__(self, user_input, email_case=False, email_price=False, email_model_id=None, user=None):
        self.user_input = user_input
        self.user = user
        self.email = email_case, email_price, email_model_id
        self.model_id = self._pin_model()
        self.tasks = self._pin_task()

    def _pin_model(self):
        # Task Email already has model created before, so escape.
        if self.email[0]:
            return self.email[2]

        new_core_model = models.FastTaskInfo(
            user_input_search=self.user_input,
            search_for=self.user
        )

        try:
            new_core_model.full_clean()
            new_core_model.save()
        except ValidationError:
            return None

        return new_core_model.id

    def _pin_task(self):
        try:
            bookstore_settings = settings.SCRAPER_BOOKSTORES
        except AttributeError:
            raise ImportError("SCRAPER_BOOKSTORES must be specified in django settings.")

        if not bookstore_settings:
            raise ValueError(f'Bookstores class name must be specified in SCRAPER_BOOKSTORES')

        mix_inheritances = tuple(
            (Task, getattr(sys.modules[__name__], import_name)) for import_name in bookstore_settings)

        bases = [type('ReadyTask', mixin_inheritance, {}) for mixin_inheritance in mix_inheritances]

        tasks_as_dict = [
            asdict(mix_class(self.model_id, self.user_input, email=self.email[0], email_price=self.email[1]))
            for mix_class in bases]

        return tasks_as_dict

    @classmethod
    def create_email_task(cls, user_input, user_email, user_price, user_id=None):
        new_email_task = models.EmailTaskInfo(
            user_input_search=user_input,
            user_email=user_email,
            user_price_alert=user_price,
            search_for_id=user_id
        )

        try:
            new_email_task.full_clean()
            new_email_task.save()
        except ValidationError:
            return False
        return new_email_task.id

    def run(self):
        celery_task_id = tasks.fast_scrap_task.apply_async([self.tasks])
        return celery_task_id


class Woblink:
    BOOKSTORE_URL = 'https://woblink.com/katalog/ebooki?szukasz='
    ALL_EBOOK_CONTAINER = 'ul.catalog-items.lista'
    EBOOK_CONTAINER = 'div [data-item-layout="tiles"]'
    EBOOK_DETAILS = {
        'author': {'qs': 'p.catalog-tile__author a', 'type': 'text'},
        'title': {'qs': 'a.catalog-tile__title span', 'type': 'text'},
        'price': {'qs': 'p.catalog-tile__new-price span', 'type': 'decimal'},
        'jpg': {'qs': '.lazy-animated', 'type': 'attribute', 'attr': 'srcset'},
        'url': {'qs': ".catalog-tile__title", 'type': 'attribute', 'attr': 'href'},
    }

    def __init__(self, user_input):
        self.user_input = user_input
        self.bookstores_url = self.get_url()

    def get_url(self):
        if len(self.user_input.split()) < 2:
            return ''.join([self.BOOKSTORE_URL, self.user_input])
        return ''.join([self.BOOKSTORE_URL, '+'.join(self.user_input.split())])


class Empik:
    BOOKSTORE_URL = 'https://www.empik.com/audiobooki-i-ebooki,35,s?q='
    ALL_EBOOK_CONTAINER = 'div.container.search-results.js-search-results'
    EBOOK_CONTAINER = 'div.search-list-item'
    EBOOK_DETAILS = {
        'author': {'qs': 'a.smartAuthor', 'type': 'text'},
        'title': {'qs': '.ta-product-title', 'type': 'text'},
        'price': {'qs': '.price.ta-price-tile', 'type': 'decimal'},
        'jpg': {'qs': '.lazy', 'type': 'attribute', 'attr': 'lazy-img'},
        'url': {'qs': '.seoTitle', 'type': 'attribute', 'attr': 'href'}
    }

    def __init__(self, user_input):
        self.user_input = user_input
        self.bookstores_url = self.get_url()

    def get_url(self):
        if len(self.user_input.split()) < 2:
            return ''.join([self.BOOKSTORE_URL, self.user_input])
        return ''.join([self.BOOKSTORE_URL, '%20'.join(self.user_input.split())])


class Publio:
    BOOKSTORE_URL = 'https://www.publio.pl/e-booki.html?keyword='
    ALL_EBOOK_CONTAINER = '.listing__products-filter-result'
    EBOOK_CONTAINER = '.v-popover.product-tail'
    EBOOK_DETAILS = {
        'author': {'qs': 'span[data-v-6045cf5e]', 'type': 'text'},
        'title': {'qs': '.title', 'type': 'text'},
        'price': {'qs': '.current', 'type': 'decimal'},
        'jpg': {'qs': '', 'type': ''},
        'url': {'qs': '', 'type': ''},
    }

    def __init__(self, user_input):
        self.user_input = user_input
        self.bookstores_url = self.get_url()

    def get_url(self):
        if len(self.user_input.split()) < 2:
            return ''.join([self.BOOKSTORE_URL, self.user_input])
        return ''.join([self.BOOKSTORE_URL, '%20'.join(self.user_input.split())])
