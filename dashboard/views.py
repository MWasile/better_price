from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from scraper import models


class DashboardHistory(ListView):
    model = models.FastTaskInfo
    context_object_name = 'user_results'
    template_name = 'dashboard/dashboard_home.html'
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('users:login'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return models.FastTaskInfo.objects.filter(search_for=self.request.user.id)


class ResultsDetail(ListView):
    model = models.ScrapEbookResult
    template_name = 'dashboard/details.html'
    context_object_name = 'details'

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return models.ScrapEbookResult.objects.filter(object_id=pk)