import asyncio
import dataclasses
from dataclasses import astuple, asdict
from dataclasses import dataclass
from decimal import Decimal

import aiohttp
import bs4


class ScrapEngine:
    async def scrap_request(self, session, task):
        async with session.get(task['url']) as response:
            html = await response.text()

        await self.prettify_response(html, task)

    @staticmethod
    async def prettify_response(data_to_prettify, task):
        t_soup = bs4.BeautifulSoup(data_to_prettify, 'lxml')
        ebook_main_container = t_soup.select_one(task['first_qs'])
        all_ebooks = ebook_main_container.select(task['second_qs'])

        for i in all_ebooks:
            title = i.select_one(task['title_qs'])
            print('aio: ', title.getText())
            return

    async def setup_task(self, tasks):
        async with aiohttp.ClientSession() as session:
            tasks_to_run = (self.scrap_request(session, task) for task in tasks)
            await asyncio.gather(*tasks_to_run)


@dataclass
class Task:
    owner_model_id: int
    user_input: str
    _: dataclasses.KW_ONLY
    _data: dict
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
            self.url = self.urls
            self.querry_selectors = {
                'BOOKSTORE_URL': self.BOOKSTORE_URL,
                'ALL_EBOOK_CONTAINER': self.ALL_EBOOK_CONTAINER,
                'EBOOK_CONTAINER': self.EBOOK_CONTAINER,
                'EBOOK_DETAIL': self.EBOOK_DETAIL
            }

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data_from_bookstores):
        if not self.email and self.email is not None:
            return

        # TODO: DB AUTOSAVE
        self._data = data_from_bookstores
