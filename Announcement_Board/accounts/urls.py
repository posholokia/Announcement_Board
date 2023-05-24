from django.urls import path
from .views import Profile, SignUp

urlpatterns = [
    path('profile/<int:pk>', Profile.as_view(), name='profile'),
    # path('signup/', SignUp.as_view(), name='signup'),
    # path('profile/<int:pk>', Profile.as_view(), name='profile'),
]