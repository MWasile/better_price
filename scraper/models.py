from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db import models
from django.contrib.contenttypes.models import ContentType


class BaseTaskInfo(models.Model):
    task_type = models.CharField(max_length=10)
    user_ebook = models.CharField(max_length=200)
    results = GenericRelation('ScrapResult')

    class Meta:
        abstract = True


class FastTaskInfo(BaseTaskInfo):
    pass


class EmailTaskInfo(BaseTaskInfo):
    email = models.EmailField(null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    status = models.BooleanField(default=True)


class ScrapResult(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    data = models.JSONField()
