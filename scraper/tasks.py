import asyncio

from celery import shared_task
from scraper import async_scraper as acs
from scraper.models import EmailTaskInfo


@shared_task(bind=True, queue='scrap_queue')
def fast_scrap_task(self, task_list):
    task_to_scrap = [
        acs.Task(
            task['owner_model_id'],
            task['user_input'],
            url=task['url'],
            querry_selectors=task['querry_selectors']) for task in task_list]

    engine = acs.ScrapEngine()
    asyncio.run(engine.setup_task(task_to_scrap))


@shared_task(queue='email_queue')
def email_task():
    available_email_task = EmailTaskInfo.objects.filter(status=True)

    for task in available_email_task:
        task_manager = acs.TaskManager(task.user_ebook, email_case=True, email_price=task.price,
                                       email_model_id=task.id)
        email_scrap_task.apply_async([task_manager.tasks])


@shared_task(queue='email_queue')
def email_scrap_task(task_list):
    email_task_to_scrap = [
        acs.Task(
            task['owner_model_id'],
            task['user_input'],
            url=task['url'],
            querry_selectors=task['querry_selectors'],
            email=True,
            email_price=task['email_price']) for task in task_list]

    engine = acs.ScrapEngine()
    asyncio.run(engine.setup_task(email_task_to_scrap))
