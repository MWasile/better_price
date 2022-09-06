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


class ScrapTaskFactory(TaskFactory):
    """
    TODO:
        1. Create task for all available bookstores
        2. Create model to agregate contentype relatons?
    """
    pass


class EmailTaskFactory(TaskFactory):
    """
    TODO:
        1. Create schedule task
        2. Crete model with status / user email / price?
        3. Send email?
    """
    pass


class Woblink(ScrapEngine):
    """
    TODO:
        core setup:
        BOOKSTORE_URL
        qs -> main ebook container
        qs -> one ebook container
        dict -> ebook detai {
                'author':
                'title':
                'price':
                'url':
                'url image?'
                            }
        method:
        1. get_url -> add %20 or sth else to url+userinput
    """
    pass


class Empik(ScrapEngine):
    pass
