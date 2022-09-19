from asgiref.sync import sync_to_async
from django.dispatch import receiver
from django.core.mail import send_mail

from . import signals
from . import models


@receiver(signals.email_success)
def email_sucess_manager(sender, task_id, scrap_data, **kwargs):
    received_data = scrap_data.get('task_data')

    task_model = models.EmailTaskInfo.objects.filter(id=received_data['id']).first()

    if task_model is not None:
        e = send_mail(
            f'[BETTER CENEO ALERT]! Ebook: {received_data["title"]}!',
            f'Your ebook price now is lower than {task_model.price}',
            'django.better.ceneo.app@gmail.com',
            [str(task_model.email)]
        )
        if e != 0:
            task_model.mark_as_done()



