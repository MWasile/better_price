from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response

from api.tasks import scrap_test


class Test(views.APIView):
    def get(self, request):
        scrap_test.apply_async()
        return Response({'Status': 'OK'})
