from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from . import forms


class RegistrationView(FormView):
    form_class = forms.RegistrationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('home:home')

    def form_valid(self, form):
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
        return super().form_valid(form)
