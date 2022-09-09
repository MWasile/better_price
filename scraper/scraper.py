import sys

from django.db import DatabaseError, IntegrityError, DataError

from config import settings
from scraper.models import Task as modelTask


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
    pass


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

    def __init__(self, user_input):
        super().__init__(user_input)


class TaskFactory:
    """
    TODO:
        1. Make class instance TASK with inh bookstores / email too
        2. Import bookstore setup from django.config -> errors?
    """
    @staticmethod
    def create_task_istance(*, task_type, user_input):
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

        tasks = [mix_class(user_input) for mix_class in tasks_base]

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
        self.model_id = self.create_task_model(task_type)

    def create_task_model(self, task_type):
        if not self.user_input_search:
            raise ValueError('User input is required as parameter. Cannot be empty string.')

        if task_type.lower() not in ['email', 'scrap']:
            raise ValueError(f'task_type must be "email" or "scrap", not {task_type}')

        try:
            new_task_model = modelTask.objects.create(
                task_type=task_type,
                search_key=self.user_input_search)
        except (TypeError, DatabaseError, IntegrityError, DataError) as err:
            raise err
        else:
            return new_task_model.id


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

