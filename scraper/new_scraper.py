import difflib
import sys

import requests
from bs4 import BeautifulSoup

from scraper.models import FastTaskInfo, ScrapResult
from django.core.exceptions import ValidationError

from config import settings


class ScrapEnginge:
    MATCH_SETTINGS = 0.80

    def scrap_request(self):
        try:
            r = requests.get(self.url)
        except requests.exceptions.RequestException:
            return False

        if r.status_code == 200:
            return r.content

        return False

    def is_match(self, arg1, arg2):
        if not difflib.SequenceMatcher(None, arg1, arg2).ratio() > self.MATCH_SETTINGS:
            return False
        return True

    def prettify_response(self, raw_data):

        tag_soup = BeautifulSoup(raw_data, 'lxml')
        prettify_response_data = []

        ebook_main_container = tag_soup.select_one(self.ALL_EBOOK_CONTAINER)

        if ebook_main_container:
            available_ebooks = ebook_main_container.select(self.EBOOK_CONTAINER)

            for ebook in available_ebooks:
                title = ebook.select_one(self.EBOOK_DETAIL['title'])

                if title and self.is_match(title.getText(), self.user_ebook):
                    prettify_response_data.append({
                        'title': title.getText(),
                        'author': ebook.select_one(self.EBOOK_DETAIL['author']).getText(),
                        'price': ebook.select_one(self.EBOOK_DETAIL['price']).getText()
                    })
                    # only one result from bookstores
                    return prettify_response_data
        return False


class Task(ScrapEnginge):
    def __init__(self, user_ebook, owner_model):
        super().__init__(user_ebook)
        self.user_ebook = user_ebook
        self.owner_model = owner_model
        self._data_auto_save = []

    @property
    def data_auto_save(self):
        return self._data_auto_save

    @data_auto_save.setter
    def data_auto_save(self, data_from_website):
        own_save = self._db_save(data_from_website)

        if own_save:
            self._data_auto_save = data_from_website
        else:
            self._data_auto_save = None

    def _db_save(self, data_to_save):

        new_model = ScrapResult(
            data=data_to_save,
            content_object=self.owner_model
        )
        new_model.save()
        return True


class FastScrapMixin:
    def scrap(self):
        raw_site_data = self.scrap_request()

        if not raw_site_data:
            return False

        ebook_detail = self.prettify_response(raw_site_data)

        if not ebook_detail:
            return False

        self.data_auto_save = ebook_detail

        return ebook_detail


class EmailScrapMixin:
    # inh -> (Task, BookstoreClass)
    # format price str -> , . zł
    # compare web price - user pirce
    # overwrite
    pass



class TaskFactory:
    @classmethod
    def create_task_istance(cls, mixin_name, user_ebook, owner_model_id):
        try:
            bookstore_settings = settings.SCRAPER_BOOKSTORES
        except AttributeError:
            raise ImportError("SCRAPER_BOOKSTORES must be specified in django settings.")

        if not bookstore_settings:
            raise ValueError(f'Bookstores class name must be specified in SCRAPER_BOOKSTORES')

        choosen_mixin = getattr(sys.modules[__name__], mixin_name)

        inheritances = tuple(
            (Task, choosen_mixin, getattr(sys.modules[__name__], import_name)) for import_name in bookstore_settings)

        task_base = [type(mixin_name, inheritance, {}) for inheritance in inheritances]

        tasks = [mix_class(user_ebook, owner_model_id) for mix_class in task_base]

        return tasks


class TaskManager(TaskFactory):
    """
    ONLY!!!!:
        1. Run fast scrap
        2. Run fast scrap based on earlier set email task
        3. Set email task without instant scrap
    """

    def __init__(self, scrap_type, user_ebook, user_email=None, user_price=None, email_case_model_id=None):
        self.user_ebook = user_ebook
        self.email_case = {'email': user_email, 'price': user_price, 'model_id': email_case_model_id}
        self.scrap_type = self._own_type(scrap_type)
        self.scrap_model = self._pin_model()
        self.tasks = self._pin_task()

    def _own_type(self, user_input_type):

        if user_input_type.lower() not in ['email', 'fast']:
            raise ValueError(f'task_type must be "email" or "fast", not {user_input_type}')

        if user_input_type.lower() == 'email':
            if not self.email_case['email']:
                raise ValueError('In email task, parameter user_email is required.')
            if not self.email_case['price']:
                raise ValueError('In email task, parameter user_price is required.')
            if not self.email_case['model_id']:
                raise ValueError('In email task, parameter email_case_model_id is required.')
            return user_input_type

        return user_input_type

    def _pin_model(self):
        if self.email_case['model_id']:
            # Task Email already has model created before, so escape.
            return self.email_case['model_id']

        if not self.user_ebook:
            return None

        new_info_model = FastTaskInfo(
            task_type=self.scrap_type,
            user_ebook=self.user_ebook
        )

        try:
            new_info_model.full_clean()
            new_info_model.save()
        except ValidationError:
            return None

        return new_info_model

    def _pin_task(self):
        if self.scrap_type == 'fast':
            mixin_type = 'FastScrapMixin'
        else:
            mixin_type = 'EmailScrapMixin'

        try:
            tasks = self.create_task_istance(mixin_type, self.user_ebook, self.scrap_model)
        except (AttributeError, ValueError) as err:
            print(err)
            return None
        return tasks

    def run_celery_task(self):
        # TODO: pass all tasks to celery worker
        return '?'

    @classmethod
    def create_email_task(cls):
        return 'model_id'


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
