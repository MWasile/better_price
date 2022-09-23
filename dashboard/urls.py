from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('home', views.DashboardHistory.as_view(), name='home'),
    path('detail/<int:pk>', views.ResultsDetail.as_view(), name='detail'),
]