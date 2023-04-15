from django.urls import path
from .views import (
    GetAuthURL,
    IsAuthenticated,
    auth_callback,
    CurrentSong,
    PlaySong,
    PauseSong,
)

urlpatterns = [
    path("get-auth-url", GetAuthURL.as_view(), name="get_url"),
    path("redirect", auth_callback, name="auth_cb"),
    path("is-authenticated", IsAuthenticated.as_view(), name="is_auth"),
    path("current-song", CurrentSong.as_view(), name="curr_song"),
    path("play", PlaySong.as_view(), name="play_song"),
    path("pause", PauseSong.as_view(), name="pause_song"),
]
