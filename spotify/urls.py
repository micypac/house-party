from django.urls import path
from .views import GetAuthURL, IsAuthenticated, auth_callback, CurrentSong

urlpatterns = [
    path("get-auth-url", GetAuthURL.as_view(), name="get_url"),
    path("redirect", auth_callback, name="auth_cb"),
    path("is-authenticated", IsAuthenticated.as_view(), name="is_auth"),
    path("current-song", CurrentSong.as_view(), name="curr_song"),
]
