import asyncio

from asgiref.sync import sync_to_async
from celery import shared_task
from scraper import async_scraper as acs


@shared_task(queue='scrap_queue')
def fast_scrap_task(task_list):
    task_to_scrap = []
    for t in task_list:
        task_to_scrap.append(
            acs.Task(t['owner_model_id'],
                     t['user_input'],
                     url=t['url'],
                     querry_selectors=t['querry_selectors'])
        )

    engine = acs.ScrapEngine()
    sync_to_async(asyncio.run(engine.setup_task(task_to_scrap)))
