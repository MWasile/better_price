import asyncio
import random

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


class Engine:
    async def scrap(self, session, task):
        async with session.get(task['url']) as response:
            html = await response.text()

        prettify = await self.prettify_response(html, task)
        return prettify

    @staticmethod
    async def prettify_response(data_to_prettify, task):
        # async def parser_html(data):
        #     tag_soup = bs4.BeautifulSoup(data, 'lxml')
        #     return tag_soup
        #
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
                tasks_to_run.append(self.scrap(session, task))

            web_result = await asyncio.gather(*tasks_to_run)




start = time.time()
test = Engine()
asyncio.run(test.setup_task(t))
print(f'aiohttp: {time.time() - start}')


class ScrapEnginge_2:
    def __init__(self, tasks):
        self.tasks = tasks

    def run_run(self):

        for t in self.tasks:
            x = self.scrap_request(t['url'])
            self.prettify_response(x, t)

    def scrap_request(self, url):
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException:
            return False

        if r.status_code == 200:
            return r.content

        return False

    def prettify_response(self, raw_data, task):
        tag_soup = bs4.BeautifulSoup(raw_data, 'lxml')

        ebook_main_container = tag_soup.select_one(task['first_qs'])
        all_ebooks = ebook_main_container.select(task['second_qs'])

        for i in all_ebooks:
            title = i.select_one(task['title_qs'])
            print('Request: ', title.getText())
            return title
        return False


start2 = time.time()
test_2 = ScrapEnginge_2(t)
test_2 = test_2.run_run()
print(f'requests: {time.time() - start2}')
