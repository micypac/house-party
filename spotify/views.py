from django.shortcuts import redirect
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from requests import Request, get, post, put
from datetime import timedelta

from .models import SpotifyToken
from api.models import Room

from .utils import invoke_spotify_api_req


class GetAuthURL(APIView):
    def get(self, req, format=None):
        scopes = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

        url = (
            Request(
                "GET",
                "https://accounts.spotify.com/authorize",
                params={
                    "client_id": settings.SPOTIFY_CLIENT_ID,
                    "response_type": "code",
                    "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
                    "scope": scopes,
                },
            )
            .prepare()
            .url
        )

        return Response({"url": url}, status=status.HTTP_200_OK)


class IsAuthenticated(APIView):
    def get(self, req, format=None):
        queryset = SpotifyToken.objects.filter(user=self.request.session.session_key)

        if queryset.exists():
            user_token = queryset[0]

            if user_token.expires_in <= timezone.now():
                refresh_token = user_token.refresh_token

                resp = post(
                    "https://accounts.spotify.com/api/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": settings.SPOTIFY_CLIENT_ID,
                        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
                    },
                ).json()

                resp_token_type = resp.get("token_type")
                resp_acc_token = resp.get("access_token")
                resp_ref_token = resp.get("refresh_token")
                resp_exp_in = resp.get("expires_in")

                converted_exp_in = timezone.now() + timedelta(seconds=resp_exp_in)

                new_token, is_created = SpotifyToken.objects.update_or_create(
                    user=self.request.session.session_key,
                    access_token=resp_acc_token,
                    refresh_token=resp_ref_token,
                    token_type=resp_token_type,
                    expires_in=converted_exp_in,
                )

            is_auth = True
        else:
            is_auth = False

        return Response({"status": is_auth}, status=status.HTTP_200_OK)


def auth_callback(request, format=None):
    code = request.GET.get("code")
    error = request.GET.get("error")

    resp = post(
        "https://accounts.spotify.com/api/token",
        data={
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        },
    ).json()

    resp_token_type = resp.get("token_type")
    resp_acc_token = resp.get("access_token")
    resp_ref_token = resp.get("refresh_token")
    resp_exp_in = resp.get("expires_in")
    resp_error = resp.get("error")

    if not request.session.exists(request.session.session_key):
        request.session.create()

    converted_exp_in = timezone.now() + timedelta(seconds=resp_exp_in)

    new_token, is_created = SpotifyToken.objects.update_or_create(
        user=request.session.session_key,
        access_token=resp_acc_token,
        refresh_token=resp_ref_token,
        token_type=resp_token_type,
        expires_in=converted_exp_in,
    )

    return redirect("frontend:home")


class CurrentSong(APIView):
    def get(self, req):
        room_code = self.request.session.get("room_code")
        queryset = Room.objects.filter(code=room_code)
        if queryset.exists():
            room = queryset[0]
        else:
            return Response(
                {"Bad Request": "Room Not Found"}, status=status.HTTP_404_NOT_FOUND
            )

        host = room.host
        endpoint = "/player/currently-playing"

        resp = invoke_spotify_api_req(host, endpoint)

        if "error" in resp or "item" not in resp:
            return Response(
                {"Bad Request": "No Content"}, status=status.HTTP_204_NO_CONTENT
            )

        item = resp.get("item")
        song_id = item.get("id")
        album_cover = item.get("album").get("images")[0].get("url")
        duration = item.get("duration_ms")
        progress = resp.get("progress_ms")
        is_playing = resp.get("is_playing")

        artists_text = ""

        for i, artist in enumerate(item.get("artists")):
            if i > 0:
                artists_text += ", "
            name = artist.get("name")
            artists_text += name

        song = {
            "title": item.get("name"),
            "artist": artists_text,
            "duration": duration,
            "time": progress,
            "img_url": album_cover,
            "is_playing": is_playing,
            "votes": 0,
            "id": song_id,
        }

        return Response(song, status=status.HTTP_200_OK)
