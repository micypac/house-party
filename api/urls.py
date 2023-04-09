from django.urls import path

from .views import RoomList

urlpatterns = [
    path("", RoomList.as_view(), name="room_list"),
]
