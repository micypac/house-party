from django.shortcuts import redirect
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from requests import Request, get, post, put
from datetime import timedelta

from .models import SpotifyToken


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
