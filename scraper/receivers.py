import asyncio

from django.dispatch import receiver
from django.core.mail import send_mail

from . import signals
from . import models
from example_channels import consumers
from channels.layers import get_channel_layer


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


@receiver(signals.do_your_job)
def do_your_job_manager(sender, channel_name, user_input, user=None, **kwargs):
    channel_layer = get_channel_layer()

    massage_to_frontend = channel_layer.send(f"{channel_name}", {
        "type": "frontend",
        "text": f"{user_input}",
    })

    go_scrap = consumers.help_runner(channel_name, user_input, user)

    loop = asyncio.get_event_loop()

    t1 = loop.create_task(massage_to_frontend)
    t2 = loop.create_task(go_scrap)
