import asyncio
import aiohttp
import time
import requests


class Engine:

    @staticmethod
    async def scrap(session, url):
        async with session.get(url) as response:
            html = await response.text()
            return html

    async def setup_task(self, tasks):
        tasks_to_run = []
        async with aiohttp.ClientSession() as session:
            for url in tasks:
                tasks_to_run.append(self.scrap(session, url))

            web_result = await asyncio.gather(*tasks_to_run)


start = time.time()
test = Engine()
t = ['https://www.google.com/',
     'https://www.wp.pl',
     'https://www.youtube.com',
     'https://www.onet.pl',
     'https://helion.pl',
     'https://www.empik.com'
     ]
asyncio.run(test.setup_task(t))
print(f'aiohttp: {time.time() - start}')


class Engine_2:
    @staticmethod
    def scrap(url):
        r = requests.get(url)
        return r.content

    def setup_task(self, tasks):
        web_result = []
        for t in tasks:
            new_r = self.scrap(t)
            web_result.append(new_r)


start = time.time()
x = Engine_2()
x.setup_task(t)
print(f'requests: {time.time() - start}')
