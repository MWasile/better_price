from celery import shared_task
import scraper.scraper as sc
from scraper.models import EmailTaskInfo


@shared_task(queue='scrap_queue')
def fast_scrap_task(task):
    tasks_to_run = sc.TaskFactory.create_task_istance(
        task['type'],
        task['user_ebook'],
        task['scrap_model']
    )

    for task in tasks_to_run:
        task.scrap()


@shared_task(queue='email_queue')
def email():
    print('zyje')
    all_tasks = EmailTaskInfo.objects.filter(status=True)

    for task in all_tasks:
        ts = sc.TaskManager('email', user_ebook=task.user_ebook,
                            email_case_model=task.id, user_price_alert=task.price)
        ts.run_celery_task()


@shared_task(queue='email_queue')
def email_send():
    all_tasks = EmailTaskInfo.objects.filter(status=None)

    for task in all_tasks:
        # TODO: send email, data -> task.results.all
        pass
