from django.db import models
from django.contrib.contenttypes.models import ContentType


class TaskWorkInfo(models.Model):
    task_type = models.CharField(max_length=10)
    search_key = models.CharField(max_length=200)
    email = models.EmailField(null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    status = models.BooleanField(default=True)


class ScrapTask(models.Model):
    owner_task = models.ForeignKey('TaskWorkInfo', on_delete=models.CASCADE, related_name='scrap_tasks')
    data = models.JSONField()
