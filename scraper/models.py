from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from django.forms import model_to_dict


class BaseInfo(models.Model):
    user_input_search = models.CharField(max_length=200)
    created = models.TimeField(auto_now=True)
    results = GenericRelation('ScrapEbookResult')
    search_for = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_related', blank=True, null=True,
                                   on_delete=models.PROTECT)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.__class__.__name__}: {self.user_input_search}'


class FastTaskInfo(BaseInfo):
    pass


class EmailTaskInfo(BaseInfo):
    user_price_alert = models.DecimalField(max_digits=8, decimal_places=2)
    user_email = models.EmailField()
    email_send_status = models.BooleanField(default=True)

    def mark_as_done(self):
        setattr(self, 'email_send_status', False)
        self.save()


class ScrapEbookResult(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    web_bookstore = models.CharField(max_length=100, blank=True, null=True)
    web_author = models.CharField(max_length=100, blank=True, null=True)
    web_title = models.CharField(max_length=200, blank=True, null=True)
    web_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
    web_url = models.URLField(max_length=250, blank=True, null=True)
    web_image_url = models.URLField(max_length=250, blank=True, null=True)
    created = models.TimeField(auto_now=True)

    def __str__(self):
        return f'{self.__class__.__name__}: Bookstore - {self.web_bookstore}'

    def to_dict(self):
        return model_to_dict(self, fields=['web_bookstore', 'web_author', 'web_title', 'web_price', 'web_url'])
