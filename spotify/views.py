from django.shortcuts import redirect
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from requests import Request, get, post, put
from datetime import timedelta

from .models import SpotifyToken, Vote
from api.models import Room

from .utils import invoke_spotify_api_req, play_song, pause_song, skip_song


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
                resp_exp_in = resp.get("expires_in")

                converted_exp_in = timezone.now() + timedelta(seconds=resp_exp_in)

                defaults = dict(
                    access_token=resp_acc_token,
                    token_type=resp_token_type,
                    expires_in=converted_exp_in,
                )

                new_token, is_created = SpotifyToken.objects.update_or_create(
                    defaults=defaults,
                    user=self.request.session.session_key,
                    refresh_token=refresh_token,
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

        votesCount = Vote.objects.filter(room=room, song_id=song_id).count()

        song = {
            "title": item.get("name"),
            "artist": artists_text,
            "duration": duration,
            "time": progress,
            "img_url": album_cover,
            "is_playing": is_playing,
            "votes": votesCount,
            "votes_needed": room.votes_to_skip,
            "id": song_id,
        }

        self.update_room_song(room, song_id)
        return Response(song, status=status.HTTP_200_OK)

    def update_room_song(self, room, song_id):
        curr_song = room.current_song

        if curr_song != song_id:
            room.current_song = song_id
            room.save(update_fields=["current_song"])

            # remove all votes when the song changes
            votes = Vote.objects.filter(room=room).delete()


class PlaySong(APIView):
    def put(self, req, format=None):
        room_code = self.request.session.get("room_code")
        room = Room.objects.filter(code=room_code)[0]

        if self.request.session.session_key == room.host or room.guest_can_pause:
            play_song(room.host)
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"Bad Request": "Unauthorized Control"}, status=status.HTTP_403_FORBIDDEN
        )


class PauseSong(APIView):
    def put(self, req, format=None):
        room_code = self.request.session.get("room_code")
        room = Room.objects.filter(code=room_code)[0]

        if self.request.session.session_key == room.host or room.guest_can_pause:
            pause_song(room.host)
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"Bad Request": "Unauthorized Control"}, status=status.HTTP_403_FORBIDDEN
        )


class SkipSong(APIView):
    def post(self, req, format=None):
        room_code = self.request.session.get("room_code")
        room = Room.objects.filter(code=room_code)[0]
        votes = Vote.objects.filter(room=room, song_id=room.current_song)
        votes_needed = room.votes_to_skip

        if (
            self.request.session.session_key == room.host
            or len(votes) + 1 >= votes_needed
        ):
            votes.delete()
            skip_song(room.host)
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        else:
            vote = Vote(
                user=self.request.session.session_key,
                room=room,
                song_id=room.current_song,
            )
            vote.save()

        return Response(
            {"Bad Request": "Unauthorized Control"}, status=status.HTTP_403_FORBIDDEN
        )
