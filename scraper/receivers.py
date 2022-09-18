from django.dispatch import receiver

from . import signals


@receiver(signals.email_success)
def done_task(sender, task_id, **kwargs):
    # TODO: Send email, set status in model
    pass
