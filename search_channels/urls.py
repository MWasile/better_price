from django.urls import path
from . import views

app_name = 'example_channels'

urlpatterns = [
    path('', views.ChannelsTraverse.as_view(), name='home')
]