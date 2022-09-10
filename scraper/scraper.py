import difflib
import re
import sys
import requests
from bs4 import BeautifulSoup

from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError, DataError

from config import settings
from scraper.models import TaskWorkInfo
from scraper.models import ScrapTask


class ScrapEngine:

    def __init__(self, task):
        self.task = task
        self.response_data = []
        self.match_settings = 0.80

    def scrap_request(self, db_save=True):
        try:
            r = requests.get(self.task.url)
        except requests.exceptions.RequestException as err:
            # TODO: errors logs? no raise
            return False

        if 300 > r.status_code >= 200:
            self.response_data = self._prettify_response(r.content, db_save)
            return True

        return False

    def is_match(self, arg1, arg2):
        if not difflib.SequenceMatcher(None, arg1, arg2).ratio() > self.match_settings:
            return False
        return True

    def _prettify_response(self, raw_data, db_save=True):
        if not raw_data:
            return False

        tag_soup = BeautifulSoup(raw_data, 'lxml')
        prettify_response_data = []

        ebook_main_container = tag_soup.select_one(self.task.ALL_EBOOK_CONTAINER)

        if ebook_main_container:
            available_ebooks = ebook_main_container.select(self.task.EBOOK_CONTAINER)

            for ebook in available_ebooks:
                title = ebook.select_one(self.task.EBOOK_DETAIL['title'])

                if title and self.is_match(title.getText(), self.task.user_input):
                    prettify_response_data.append({
                        'title': title.getText(),
                        'author': ebook.select_one(self.task.EBOOK_DETAIL['author']).getText(),
                        'price': ebook.select_one(self.task.EBOOK_DETAIL['price']).getText()
                    })
                    # only one result from bookstores
                    break

        if db_save:
            self.task.data_auto_save = prettify_response_data

        return prettify_response_data

    def email_result(self, user_price):

        result = []

        for ebook in self.response_data:
            if 'price' in ebook:
                try:
                    web_price = ebook['price'].replace(",", '.')
                    web_price = web_price[:re.search(r'[a-zA-Z]', ebook['price']).start()]
                    if float(web_price) <= user_price:
                        result.append(ebook)

                except Exception as err:
                    print(err)

        if not result:
            return False

        return result


class Task:

    def __init__(self, user_input, owner_model_id):
        super().__init__(user_input)
        self.owner_model_id = owner_model_id
        self._data_auto_save = {}

    @property
    def data_auto_save(self):
        return self._data_auto_save

    @data_auto_save.setter
    def data_auto_save(self, data_from_scrap):
        own_save = self._db_save(data_from_scrap)
        if own_save:
            self._data_auto_save = data_from_scrap

    def _db_save(self, data_to_save):
        new_scrap_task = ScrapTask(
            owner_task_id=self.owner_model_id,
            data=data_to_save
        )

        try:
            new_scrap_task.full_clean()
            new_scrap_task.save()
        except ValidationError:
            return False
        return True


class TaskFactory:

    @staticmethod
    def create_task_istance(*, task_type, user_input, owner_model_id):
        try:
            bookstore_settings = settings.SCRAPER_BOOKSTORES
        except AttributeError:
            raise ImportError("SCRAPER_BOOKSTORES must be specified in django settings.")

        if not bookstore_settings:
            raise ValueError(f'Bookstores class name must be specified in SCRAPER_BOOKSTORES')

        if task_type not in ['ScrapyTask', 'EmailTask']:
            raise ValueError(f'task_type must be "ScrapyTask" or "EmailTask", not {task_type}')

        core_inheritance = getattr(sys.modules[__name__], 'Task')

        # Mix inheritance -> tuple(bookstoreclass spec in dj.settings / core task class)
        # TODO: add import modules if remove bookstoresclass from this file
        inheritances = \
            tuple(
                (core_inheritance, getattr(sys.modules[__name__], import_name)) for import_name in bookstore_settings)

        # Create ScrapyTask/EmailTask class object, based on specify bookstores inheritance.
        tasks_base = [type(task_type, inheritance, {}) for inheritance in inheritances]

        # Create class instanction, with innit based on user_input

        tasks = [mix_class(user_input, owner_model_id) for mix_class in tasks_base]

        return tasks


class TaskManager(TaskFactory):

    def __init__(self, task_type, user_input_search, email=None, price=None):
        self.user_input_search = user_input_search
        self.emial_case = (email, price)
        self.task_type = self._type_validation(task_type)
        self.model_id = self._create_task_model()
        self.tasks = self._pin_tasks()

    def _type_validation(self, input_task_type):
        if input_task_type not in ['ScrapyTask', 'EmailTask']:
            raise ValueError(f'task_type must be "ScrapyTask" or "EmailTask", not {self.task_type}')

        if input_task_type == 'EmailTask':
            if not self.emial_case[0]:
                raise ValueError('In EmailTask, parameter email is required.')
            elif not self.emial_case[1]:
                raise ValueError('In EmailTask, parameter price is required.')

        if input_task_type == 'ScrapyTask':
            if self.emial_case[0]:
                raise ValueError('ScrapyTask allowed only task_type and user_input_search parameters.')

        return input_task_type

    def _create_task_model(self):
        if not self.user_input_search:
            raise ValueError('User input is required as parameter. Cannot be empty string.')

        try:
            new_task_model = TaskWorkInfo.objects.create(
                task_type=self.task_type,
                search_key=self.user_input_search,
                email=self.emial_case[0],
                price=self.emial_case[1],
            )
        except (TypeError, DatabaseError, IntegrityError, DataError) as err:
            raise err
        return new_task_model.id

    def _pin_tasks(self):
        # escape when task_type = mail
        if self.emial_case[0]:
            return True

        try:
            new_tasks = self.create_task_istance(
                task_type=self.task_type,
                user_input=self.user_input_search,
                owner_model_id=self.model_id
            )
        except (AttributeError, ValueError) as err:
            print(err, 'Error while creating class instance.')
            raise err
        return new_tasks

    def run_tasks(self):
        for task in self.tasks:
            scrap = ScrapEngine(task)
            scrap.scrap_request()

    def run_email_tasks(self, user_prince):

        ebooks_price_lower = []

        for task in self.tasks:
            scrap = ScrapEngine(task)
            scrap.scrap_request(db_save=False)
            email_results = scrap.email_result(user_prince)

            if email_results:
                ebooks_price_lower.append(email_results)

        if not ebooks_price_lower:
            return False
        return ebooks_price_lower


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
        self.url = self.get_url()

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
        self.url = self.get_url()

    def get_url(self):
        if len(self.user_input.split()) < 2:
            return ''.join([self.BOOKSTORE_URL, self.user_input])
        return ''.join([self.BOOKSTORE_URL, '%20'.join(self.user_input.split())])
