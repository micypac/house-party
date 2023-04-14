from django.urls import path
from .views import index

app_name = "frontend"

urlpatterns = [
    path("", index, name="home"),
    path("create", index),
    path("join", index),
    path("room/<str:roomCode>", index),
]
