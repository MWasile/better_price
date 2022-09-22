from asgiref.sync import sync_to_async
from django.dispatch import receiver
from django.core.mail import send_mail

from . import signals
from . import models


@receiver(signals.email_success)
def email_sucess_manager(sender, scrap_data, **kwargs):
    task_model = models.EmailTaskInfo.objects.filter(id=scrap_data['id']).first()

    if task_model is not None:
        e = send_mail(
            f'[BETTER CENEO ALERT]! Ebook: {scrap_data["task_info"]["title"]}',
            f'Your ebook price now is lower than {task_model.user_price_alert}$! \n'
            f'{scrap_data["task_info"]["url"]}',
            'django.better.ceneo.app@gmail.com',
            [str(task_model.user_email)]
        )
        if e != 0:
            task_model.mark_as_done()



