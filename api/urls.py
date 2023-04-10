from django.urls import path

from .views import RoomList, CreateRoomView

urlpatterns = [
    path("room", RoomList.as_view(), name="room_list"),
    path("create-room", CreateRoomView.as_view(), name="room_create"),
]
