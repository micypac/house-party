from .models import SpotifyToken
from requests import get, post, put

BASE_URL = "https://api.spotify.com/v1/me"


def invoke_spotify_api_req(session_id, endpoint, _post=False, _put=False):
    queryset = SpotifyToken.objects.filter(user=session_id)
    if queryset.exists():
        user_token = queryset[0]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {user_token.access_token}",
        }

        if _post:
            post(BASE_URL + endpoint, headers=headers)
        elif _put:
            put(BASE_URL + endpoint, headers=headers)
        else:
            resp = get(BASE_URL + endpoint, headers=headers)

        try:
            return resp.json()
        except:
            return {"Error": "Issue with GET Request"}
