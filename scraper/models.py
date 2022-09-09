from django.db import models
from django.contrib.contenttypes.models import ContentType


class Task(models.Model):
    task_type = models.CharField(max_length=10)
    search_key = models.CharField(max_length=200)


class BaseTask(models.Model):

    owner_task = models.ForeignKey('Task', on_delete=models.CASCADE,
                                   related_name='%(class)s',
                                   related_query_name='%(class)s_related')
    data = models.JSONField()

    class Meta:
        abstract = True


class ScrapTask(BaseTask):
    pass


class EmailTask(BaseTask):
    pass
