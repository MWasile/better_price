import random

from celery import shared_task
from api.models import ScrapTask, ScheduleTest


@shared_task(queue='scrap_queue')
def scrap_test():
    x = ScrapTask.objects.create(scrap_id='XDDD')
    x.save()


@shared_task(queue='email_queue')
def email():
    x = ScheduleTest.objects.create(sth=1)
    x.save()
