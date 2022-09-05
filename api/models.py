from django.db import models


class ScrapTask(models.Model):
    scrap_id = models.CharField(max_length=100)


class ScheduleTest(models.Model):
    sth = models.IntegerField()
