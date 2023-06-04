from django.urls import path
from .views import Profile
from allauth.account import views

urlpatterns = [
    path('profile/<int:pk>/', Profile.as_view(), name='profile'),
]