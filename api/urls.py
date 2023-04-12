from django.urls import path

from .views import (
    RoomList,
    CreateRoom,
    RoomDetail,
    JoinRoom,
    UserInRoom,
    LeaveRoom,
    UpdateRoom,
)

urlpatterns = [
    path("room", RoomList.as_view(), name="room_list"),
    path("create-room", CreateRoom.as_view(), name="room_create"),
    # path("get-room", RoomDetail.as_view(), name="room_detail"),
    path("get-room/<str:code>/", RoomDetail.as_view(), name="room_detail"),
    path("join-room", JoinRoom.as_view(), name="room_join"),
    path("user-in-room", UserInRoom.as_view(), name="user_in_room"),
    path("leave-room", LeaveRoom.as_view(), name="leave_room"),
    path("update-room", UpdateRoom.as_view(), name="room_update"),
]
