import asyncio
import random

import aiohttp
import time
import requests
import bs4


class Engine:

    async def scrap(self, session, url):
        async with session.get(url) as response:
            html = await response.text()
            beatiful_html = await self.prettify_response(html)
            return beatiful_html

    @staticmethod
    async def prettify_response(raw_data):
        async def parser_job(data_to_parse):
            tag_soup = bs4.BeautifulSoup(data_to_parse, 'lxml')
            one_div = tag_soup.select_one('title')
            return one_div

        x = await parser_job(raw_data)
        return x

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
