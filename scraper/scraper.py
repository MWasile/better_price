import sys
from dataclasses import dataclass
from abc import ABC, ABCMeta, abstractmethod

from config import settings


class ScrapEngine(ABC):
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
        self.user_inputt = user_input


class TaskFactory(metaclass=ABCMeta):
    """
    TODO:
        1. Make class instance TASK with inh bookstores / email too
        2. Import bookstore setup from django.config -> errors?
    """

    @abstractmethod
    def create_task_istance(user_input):

        bookstore_settings = settings.SCRAPER_BOOKSTORES

        if not bookstore_settings:
            return False

        core_inheritance = getattr(sys.modules[__name__], 'Task')
        inheritances = \
            tuple(
                (core_inheritance, getattr(sys.modules[__name__], import_name)) for import_name in bookstore_settings)

        tasks = []

        for inheritance in inheritances:
            tasks.append(
                type(
                    'ReadyTask',
                    inheritance,
                    {'__init__': user_input}
                ))

        return tasks


class TaskManager(TaskFactory, ABC):
    """
    TODO:
        1. Create task for all available bookstores
        2. Create model to agregate contentype relatons?
    """
    pass


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

    def __init__(self, test):
        self.test = test


x = TaskFactory.create_task_istance('Maciej')

for i in x:
    print(vars(i))
    print('*' * 10)
