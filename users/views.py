from django.contrib.auth import authenticate, login
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


class LoginView(FormView):
    form_class = forms.LoginForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('home:home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(self.request, user)
                return super().form_valid(form)
        else:
            return super().form_invalid(form)
