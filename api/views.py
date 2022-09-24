from django.core.exceptions import ValidationError
from django.shortcuts import render
from rest_framework import views, status
from rest_framework.response import Response
from scraper import tasks
from scraper import models


class CreateEmailTask(views.APIView):
    def post(self, request, title, price):

        if request.user.is_authenticated:
            email = models.EmailTaskInfo(
                user_input_search=title,
                user_price_alert=price,
                user_email=request.user.email,
                search_for=self.request.user
            )

            try:
                email.full_clean()
                email.save()
            except ValidationError:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_401_UNAUTHORIZED)
