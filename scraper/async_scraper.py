import asyncio
import random
from dataclasses import astuple, asdict
from dataclasses import dataclass

import aiohttp
import time
import bs4
import requests

woblink = {
    'url': 'https://woblink.com/katalog/ebooki?szukasz=korepetytor',
    'first_qs': 'ul.catalog-items.lista',
    'second_qs': 'div [data-item-layout="tiles"]',
    'title_qs': 'a.catalog-tile__title span',
}
empik = {
    'url': 'https://www.empik.com/audiobooki-i-ebooki,35,s?q=korepetytor&qtype=basicForm',
    'first_qs': 'div.container.search-results.js-search-results',
    'second_qs': 'div.search-list-item',
    'title_qs': '.ta-product-title',
}

t = [woblink, empik]


class ScrapEngine:

    async def scrap_request(self, session, task):
        async with session.get(task['url']) as response:
            html = await response.text()

        prettify = await self.prettify_response(html, task)
        return prettify

    @staticmethod
    async def prettify_response(data_to_prettify, task):
        async def parser_html(data):
            tag_soup = bs4.BeautifulSoup(data, 'lxml')
            return tag_soup

        # t_soup = await parser_html(data_to_prettify)
        t_soup = bs4.BeautifulSoup(data_to_prettify, 'lxml')
        ebook_main_container = t_soup.select_one(task['first_qs'])
        all_ebooks = ebook_main_container.select(task['second_qs'])

        for i in all_ebooks:
            title = i.select_one(task['title_qs'])
            print('aio: ', title.getText())
            return title

    async def setup_task(self, tasks):
        tasks_to_run = []
        async with aiohttp.ClientSession() as session:
            for task in tasks:
                tasks_to_run.append(self.scrap_request(session, task))

            web_result = await asyncio.gather(*tasks_to_run)


class TaskFactory:
    @classmethod
    def cls_to_data_class(cls):
        pass

    @classmethod
    def dict_to_data_class(cls):
        pass


test_result = []

for i in range(0, 50):
    start = time.time()
    l = ScrapEngine()
    asyncio.run(l.setup_task(t))
    end = time.time() - start
    test_result.append(end)

print('[Test results] =>', test_result)
www = sum(test_result) / len(test_result)

print('Ave:', www)
