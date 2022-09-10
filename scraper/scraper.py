import sys
import requests

from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError, DataError

from config import settings
from scraper.models import Task as modelTask, ScrapTask


class ScrapEngine:
    """
    TODO:
        1. Erorr handler?
        2. Do Request -> local ip / PARAMS: Task obj
        3. Do Request -> proxy / fake user agent / PARAMS: Task obj
        4. Extract data -> bs4 /
        5. Detail scrap (email alert) / PARAMS: Task obj
        6. Check result from site match user input -> difflib.SequenceMatcher
    """

    def __init__(self):
        self.response_raw_data = str

    def scrap_request(self):
        try:
            r = requests.get(self.url)
        except requests.exceptions.RequestException as err:
            return False

        if 300 > r.status_code >= 200:
            self.response_raw_data = r.content
            return True

        return False


class Task:
    """
    TODO:
        1. db self save?
        2. data class?
        Params:
        task_id: int?
        main_task_id -> model create in ScrapTaskFactory (!!!contnttype!!!)
        task_keyword: str
        status_flag: Boolean
        data_from_site: dict
    """

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
    """
    TODO:
        1. Make class instance TASK with inh bookstores / email too
        2. Import bookstore setup from django.config -> errors?
    """

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
    """
    TODO:
        1. Create task for all available bookstores
        2. Create model to agregate contentype relatons?
    """

    def __init__(self, task_type, user_input_search):
        super().__init__()
        self.user_input_search = user_input_search
        self.task_type = task_type
        self.model_id = self._create_task_model()
        self.tasks = self._pin_tasks()

    def _create_task_model(self):
        if not self.user_input_search:
            raise ValueError('User input is required as parameter. Cannot be empty string.')

        if self.task_type.lower() not in ['emailtask', 'scrapytask']:
            raise ValueError(f'task_type must be "ScrapyTask" or "EmailTask", not {self.task_type}')

        try:
            new_task_model = modelTask.objects.create(
                task_type=self.task_type,
                search_key=self.user_input_search
            )
        except (TypeError, DatabaseError, IntegrityError, DataError) as err:
            raise err
        return new_task_model.id

    def _pin_tasks(self):
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


class Woblink(ScrapEngine):
    """
    TODO:
        core setup:
        BOOKSTORE_URL               DONE
        qs -> main ebook container  DONE
        qs -> one ebook container   DONE
        dict -> ebook detai {       NOT YET
                'author':           DONE
                'title':            DONE
                'price':            DONE
                'url':              NOT YET
                'url image?'        NOT YET
                            }
        method:
        1. get_url -> add %20 or sth else to url+userinput DONE
    """

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
        super().__init__()
        self.user_input = user_input
        self.url = self.get_url()

    def get_url(self):
        if len(self.user_input.split()) < 2:
            return ''.join([self.BOOKSTORE_URL, self.user_input])
        return ''.join([self.BOOKSTORE_URL, '+'.join(self.user_input.split())])


class Empik(ScrapEngine):
    BOOKSTORE_URL = 'XDDDD'

    def __init__(self, user_input):
        self.user_input = user_input
        self.url = 'XD'
