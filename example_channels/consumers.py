import asyncio
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from scraper.async_scraper import TaskManager, ScrapEngine


class EbookHelper:
    """
    JS -> USER INPUT -> CTX
    CTX -> DATA -> JS
    CTX -> END -> JS
    """
    def __init__(self, consumer, **kwargs):
        self.consumer = consumer
        self.data_from_user = kwargs
        self.celery_task_id = None

    async def __aenter__(self, consumer):
        self.consumer = consumer
        return self

    async def __aexit__(self, *args, **kwargs):
        pass


class SimpleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        await self.close()

    async def receive(self, text_data=None, **kwargs):
        data = json.loads(text_data)

        x = await sync_to_async(TaskManager)('XD')

        async with EbookHelper(data, consumer=self) as helper:
            pass
