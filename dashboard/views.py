from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, ListView
from scraper import models


class DashboardHome(ListView):
    model = models.FastTaskInfo
    context_object_name = 'user_results'
    template_name = 'dashboard/dashboard_home.html'
    paginate_by = 2

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('users:login'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return models.FastTaskInfo.objects.filter(search_for=self.request.user.id)