from django.urls import path

from .views import RoomList, CreateRoomView, RoomDetail, JoinRoomView, UserInRoom

urlpatterns = [
    path("room", RoomList.as_view(), name="room_list"),
    path("create-room", CreateRoomView.as_view(), name="room_create"),
    # path("get-room", RoomDetail.as_view(), name="room_detail"),
    path("get-room/<str:code>/", RoomDetail.as_view(), name="room_detail"),
    path("join-room", JoinRoomView.as_view(), name="room_join"),
    path("user-in-room", UserInRoom.as_view(), name="user_in_room"),
]
