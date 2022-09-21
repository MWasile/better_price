from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models




class BaseInfo(models.Model):
    user_input_search = models.CharField(max_length=200)
    created = models.TimeField(auto_now=True)
    results = GenericRelation('ScrapEbookResult')
    search_for = models.ForeignKey(User, related_name='%(class)s_related', blank=True, null=True,
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
    email_send_status = models.BooleanField(default=False)

    def mark_as_done(self):
        setattr(self, 'email_send_status', True)
        self.save()


class ScrapEbookResult(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    web_bookstore = models.CharField(max_length=100)
    web_author = models.CharField(max_length=100)
    web_title = models.CharField(max_length=200)
    web_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
    web_url = models.URLField(max_length=250)
    web_image_url = models.URLField(max_length=250)
    created = models.TimeField(auto_now=True)

    def __str__(self):
        return f'{self.__class__.__name__}: Bookstore - {self.web_bookstore}'
