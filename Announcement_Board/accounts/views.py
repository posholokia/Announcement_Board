from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from .forms import SignUpForm


class SignUp(CreateView):
    model = User
    form_class = SignUpForm
    success_url = '/accounts/login'
    template_name = 'registration/signup.html'


class Profile(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'lk.html'
    context_object_name = 'profile'