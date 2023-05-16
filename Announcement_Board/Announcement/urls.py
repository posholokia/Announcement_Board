from django.urls import path
from .views import *


urlpatterns = [
    path('board/create/', CreateAnnouncement.as_view(), name='create'),
    path('board/<int:pk>/', DetailAnnouncement.as_view(), name='announce'),
    path('board/my_announcement/', MyAnnounce.as_view(), name='my_announce'),
    path('board/', AnnouncementList.as_view(), name='list'),
    path('board/<str:category>/', AnnouncementList.as_view(), name='category'),
    path('board/<int:pk>/edit/', UpdateAnnouncement.as_view(), name='edit'),
    path('board/<int:pk>/response', AddResponse.as_view(), name='add_response'),
    path('board/<int:pk>/remove_response', remove_response, name='remove_response'),
    path('board/my_announcement/responses', ResponseList.as_view(), name='my_responses'),

]
