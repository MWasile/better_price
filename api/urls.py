from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('test/<str:title>/<int:price>', views.CreateEmailTask.as_view(), name='email')
]