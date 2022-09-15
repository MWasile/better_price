import asyncio
import random

import aiohttp
import time
import bs4
import requests


class Engine:
    async def scrap(self, session, url):
        async with session.get(url) as response:
            html = await response.text()

        prettify = await self.prettify_response(html)
        return prettify

    @staticmethod
    async def prettify_response(data_to_prettify):
        # async def parser_html(data):
        #     tag_soup = bs4.BeautifulSoup(data, 'lxml')
        #     return tag_soup
        #
        # t_soup = await parser_html(data_to_prettify)
        t_soup = bs4.BeautifulSoup(data_to_prettify, 'lxml')
        ebook_main_container = t_soup.select_one('ul.catalog-items.lista')
        all_ebooks = ebook_main_container.select('div [data-item-layout="tiles"]')

        for i in all_ebooks:
            title = i.select_one('a.catalog-tile__title span')
            return title

    async def setup_task(self, tasks):
        tasks_to_run = []
        async with aiohttp.ClientSession() as session:
            for url in tasks:
                tasks_to_run.append(self.scrap(session, url))

            web_result = await asyncio.gather(*tasks_to_run)
            print(web_result)


t = ['https://woblink.com/katalog/ebooki?szukasz=korepetytor']

random.shuffle(t)

start = time.time()
test = Engine()
asyncio.run(test.setup_task(t))
print(f'aiohttp: {time.time() - start}')


class ScrapEnginge_2:

    def scrap_request(self, url):
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException:
            return False

        if r.status_code == 200:
            return r.content

        return False

    def prettify_response(self, raw_data):
        tag_soup = bs4.BeautifulSoup(raw_data, 'lxml')

        ebook_main_container = tag_soup.select_one('ul.catalog-items.lista')
        all_ebooks = ebook_main_container.select('div [data-item-layout="tiles"]')

        for i in all_ebooks:
            title = i.select_one('a.catalog-tile__title span')
            return title
        return False


start2 = time.time()
test_2 = ScrapEnginge_2()
raw_data = test_2.scrap_request(t[0])
x = test_2.prettify_response(raw_data)
print(x)
print(f'requests: {time.time() - start2}')