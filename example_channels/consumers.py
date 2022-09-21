import asyncio
import json
from enum import Enum

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from scraper.async_scraper import TaskManager
from celery.result import AsyncResult
from scraper.models import FastTaskInfo


class Massage(Enum):
    BOOKSTORES_NUMBER = 1
    TASK_DATA = 2
    END = 3


class EbookHelper:

    def __init__(self, consumer, data_from_user):
        self.consumer = consumer
        self.data_from_user = data_from_user
        self.celery_task_id = None
        self.count_bookstores = None
        self.scrap_owner_model_id = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.push_to_frontend(Massage.END)

    @sync_to_async
    def run_celery_scrap_task(self):
        new_task = TaskManager(self.data_from_user['massage'])
        self.scrap_owner_model_id = new_task.model_id
        self.count_bookstores = len(new_task.tasks)
        self.celery_task_id = new_task.run()

    @database_sync_to_async
    def get_data_from_db(self):
        results_from_db = FastTaskInfo.objects.get(pk=self.scrap_owner_model_id).results.all()
        data_to_push = [info_model.data for info_model in results_from_db]
        return data_to_push

    async def wait_until_celery_task_is_done(self):
        res = AsyncResult(str(self.celery_task_id))

        while not res.ready():
            await asyncio.sleep(0.1)

        return True

    async def push_to_frontend(self, massage_type, data=''):
        await self.consumer.send(text_data=json.dumps(
            {'massage': massage_type.value,
             f'data': f'{data}'}
        ))

    async def recieve_management(self):

        await self.run_celery_scrap_task()

        if self.celery_task_id is None:
            raise

        await self.push_to_frontend(Massage.BOOKSTORES_NUMBER, data=self.count_bookstores)

        if await self.wait_until_celery_task_is_done():
            results = await self.get_data_from_db()
            await self.push_to_frontend(Massage.TASK_DATA, data=results)


class SimpleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        await self.close()

    async def receive(self, text_data=None, **kwargs):
        data = json.loads(text_data)

        async with EbookHelper(self, data) as helper:
            await helper.recieve_management()
