from django.urls import path
from .views import CreateAnnouncement, DetailAnnouncement, AnnouncementList, UpdateAnnouncement, Response, \
    remove_response


urlpatterns = [
    path('board/create/', CreateAnnouncement.as_view(), name='create'),
    path('board/<int:pk>/', DetailAnnouncement.as_view(), name='announce'),
    path('board/', AnnouncementList.as_view(), name='list'),
    path('board/<int:pk>/edit/', UpdateAnnouncement.as_view(), name='edit'),
    path('board/<int:pk>/response', Response.as_view(), name='response'),
    path('board/<int:pk>/remove_response', remove_response, name='remove_response'),
]
