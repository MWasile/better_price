from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from scraper import tasks


class Test(views.APIView):
    def get(self, request):
        return Response({'Status': 'OK'})
