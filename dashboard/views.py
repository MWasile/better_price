from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class DashboardHome(TemplateView):
    template_name = 'dashboard/dashboard_home.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('users:login'))
        return super().get(request, *args, **kwargs)

