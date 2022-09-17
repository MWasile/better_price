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
        self.urls = self.get_url()

    def get_url(self):
        if len(self.user_input.split()) < 2:
            return ''.join([self.BOOKSTORE_URL, self.user_input])
        return ''.join([self.BOOKSTORE_URL, '%20'.join(self.user_input.split())])


@dataclass
class Task:
    owner_model_id: int
    user_input: str
    data: dict
    _: dataclasses.KW_ONLY
    email_price: Decimal = False
    url: str = None
    querry_selectors: dict = None

    def __post_init__(self):
        # In celery, this class is initiated without any inheritance, but in Task Manager he needs to be mixed with
        # any bookstore class. If mixed, we need to grab necessary class attribute as url or queryselectors because
        # we are using 'asdict' when passing this class as args to Celery Worker.
        if 'obiect' not in self.__class__.__bases__:
            super().__init__(self.user_input)
            self.url = self.urls
            self.querry_selectors = {
                'BOOKSTORE_URL': self.BOOKSTORE_URL,
                'ALL_EBOOK_CONTAINER': self.ALL_EBOOK_CONTAINER,
                'EBOOK_CONTAINER': self.EBOOK_CONTAINER,
                'EBOOK_DETAIL': self.EBOOK_DETAIL
            }



test = Task(1, 'Korepetytor', {})
print(asdict(test))
