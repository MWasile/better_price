from django.shortcuts import render
from django.views.generic import TemplateView


class ChannelsTraverse(TemplateView):
    template_name = 'example_channels/training.html'
