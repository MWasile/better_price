from django.db import models


class ScrapyTask:
    user_input = models.CharField(max_length=200)
    status = models.BooleanField()
    # results = contnttype TASK!!!


class EmailTask:
    user_input = models.CharField(max_length=200)
    status = models.BooleanField()
    user_email = models.EmailField()
    price_check = models.PositiveIntegerField()
    # results = contnttype TASK!!!


class Task:
    # task_id = links to parents /\
    user_input = models.CharField(max_length=200)
    status = models.BooleanField()
    # TODO:
    #   JSONField ? check how it works!
    scrap_data = models.JSONField()
