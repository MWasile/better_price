import asyncio
import random
from dataclasses import astuple, asdict
from dataclasses import dataclass

import aiohttp
import time
import bs4
import requests


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

        t_soup = await parser_html(data_to_prettify)
        # t_soup = bs4.BeautifulSoup(data_to_prettify, 'lxml')
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
                tasks_to_run.append(self.scrap(session, task))

            web_result = await asyncio.gather(*tasks_to_run)


@dataclass
class Task:
    owner_model_id: int
    site_url: str
    querry_selectors: dict

    def __post_init__(self):
        super(Task, self).__init__('XD')
    

class Empik:
    def __init__(self):
        self.url = 'XDD'


inheritances = Task, Empik

scrap_task = type('ScrapTask', inheritances, {})
test = scrap_task(**{'owner_model_id': 'XD', 'site_url': 'XDDD', 'querry_selectors': {}})
print(dir(test))