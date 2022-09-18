import asyncio
import dataclasses
import sys
from dataclasses import astuple, asdict
from dataclasses import dataclass
from decimal import Decimal

import socket
import aiohttp
import bs4
from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from config import settings
from scraper.models import FastTaskInfo, EmailTaskInfo, ScrapResult
from scraper.tasks import fast_scrap_task


class ScrapEngine:

    async def scrap_request(self, session, task):
        async with session.get(task.url) as response:
            html = await response.text()

        data = await self.prettify_response(html, task)
        await task.self_save(data)

    @staticmethod
    async def prettify_response(data_to_prettify, task):
        t_soup = bs4.BeautifulSoup(data_to_prettify, 'lxml')
        ebook_main_container = t_soup.select_one(task.querry_selectors['ALL_EBOOK_CONTAINER'])
        all_ebooks = ebook_main_container.select(task.querry_selectors['EBOOK_CONTAINER'])

        for i in all_ebooks:
            title = i.select_one(task.querry_selectors['EBOOK_DETAIL']['title'])
            return title.getText()

    async def setup_task(self, tasks):
        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks_to_run = (self.scrap_request(session, task) for task in tasks)
            await asyncio.gather(*tasks_to_run)


@dataclass
class Task:
    owner_model_id: int
    user_input: str
    _: dataclasses.KW_ONLY
    data: dict = None
    url: str = None
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
            self.querry_selectors = {
                'BOOKSTORE_URL': self.bookstores_url,
                'ALL_EBOOK_CONTAINER': self.ALL_EBOOK_CONTAINER,
                'EBOOK_CONTAINER': self.EBOOK_CONTAINER,
                'EBOOK_DETAIL': self.EBOOK_DETAIL
            }

    async def self_save(self, data_from_bookstores):
        @sync_to_async
        def wrapper():

            ct = ContentType.objects.get(app_label='scraper', model='fasttaskinfo')
            new_model = ScrapResult(
                    data=data_from_bookstores,
                    content_type=ct,
                    object_id=self.owner_model_id
                )

            try:
                new_model.save()
            except ValidationError:
                return None

        await wrapper()


class TaskManager:
    def __init__(self, user_input, email_case=False, email_price=False, email_model_id=None):
        self.user_input = user_input
        self.email = email_case, email_price, email_model_id
        self.model_id = self._pin_model()
        self.tasks = self._pin_task()

    def _pin_model(self):
        # Task Email already has model created before, so escape.
        if self.email[0]:
            return self.email[2]

        new_core_model = FastTaskInfo(
            task_type='fast',
            user_ebook=self.user_input
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

        tasks = [asdict(mix_class(self.model_id, self.user_input, email=self.email[0], email_price=self.email[1]))
                 for mix_class in bases]

        return tasks

    @classmethod
    def create_email_task(cls, user_input, user_email, user_price):
        new_email_task = EmailTaskInfo(
            task_type='email',
            user_ebook=user_input,
            email=user_email,
            price=user_price
        )

        try:
            new_email_task.full_clean()
            new_email_task.save()
        except ValidationError:
            return False
        return new_email_task.id

    def run(self):
        fast_scrap_task.apply_async([self.tasks])


class Woblink:
    BOOKSTORE_URL = 'https://woblink.com/katalog/ebooki?szukasz='
    ALL_EBOOK_CONTAINER = 'ul.catalog-items.lista'
    EBOOK_CONTAINER = 'div [data-item-layout="tiles"]'
    EBOOK_DETAIL = {
        'author': 'p.catalog-tile__author a',
        'title': 'a.catalog-tile__title span',
        'price': 'p.catalog-tile__new-price span',
        # TODO direclink, url_image
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
    EBOOK_DETAIL = {
        'author': 'a.smartAuthor',
        'title': '.ta-product-title',
        'price': '.price.ta-price-tile',
        # TODO direclink, url_image
    }

    def __init__(self, user_input):
        self.user_input = user_input
        self.bookstores_url = self.get_url()

    def get_url(self):
        if len(self.user_input.split()) < 2:
            return ''.join([self.BOOKSTORE_URL, self.user_input])
        return ''.join([self.BOOKSTORE_URL, '%20'.join(self.user_input.split())])
