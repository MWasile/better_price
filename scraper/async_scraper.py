import asyncio
import random

import aiohttp
import time
import requests
import bs4


class Engine:
    info = 0

    async def scrap(self, session, url):
        async with session.get(url) as response:
            print('scrap_in_with')
            html = await response.text()

        beatiful_html = await self.parser_job(html)
        title = await self.search_title(beatiful_html)
        return title

    @staticmethod
    async def parser_job(data_to_parse):
        print('parser_job')
        await asyncio.sleep(1)

        async def inside_parser_job(data):
            print('inside_parser_job')
            tag_soup = bs4.BeautifulSoup(data, 'lxml')
            return tag_soup

        return await inside_parser_job(data_to_parse)

    @staticmethod
    async def search_title(tag_soup):
        print('search_title')
        return tag_soup.select_one('title')

    async def setup_task(self, tasks):
        tasks_to_run = []
        async with aiohttp.ClientSession() as session:
            for url in tasks:
                tasks_to_run.append(self.scrap(session, url))

            web_result = await asyncio.gather(*tasks_to_run)
            print(web_result)


t = ['https://www.google.com/',
     'https://www.wp.pl',
     'https://www.youtube.com',
     'https://www.onet.pl',
     'https://helion.pl',
     'https://www.empik.com'
     ]

random.shuffle(t)

start = time.time()
test = Engine()
asyncio.run(test.setup_task(t))
print(f'aiohttp: {time.time() - start}')
