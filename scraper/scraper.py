from dataclasses import dataclass
from abc import ABC

from django.conf import settings


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


class TaskFactory(ABC):
    """
    TODO:
        1. Make class instance TASK with inh bookstores / email too
        2. Import bookstore setup from django.config -> errors?
    """
    pass


@dataclass
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
    pass


class TaskManager(TaskFactory):
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

    def __init__(self, search_ebook_name):
        super().__init__()
        self.search_ebook_name = search_ebook_name
        self.url = self.get_url()

    def get_url(self):
        if len(self.search_ebook_name.split()) < 2:
            return ''.join([self.BOOKSTORE_URL, self.search_ebook_name])
        return ''.join([self.BOOKSTORE_URL, '+'.join(self.search_ebook_name.split())])


class Empik(ScrapEngine):
    pass
