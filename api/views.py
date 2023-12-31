from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Room
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer

import sys


# class RoomList(generics.ListCreateAPIView):
class RoomList(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


# class RoomDetail(APIView):
#     serializer_class = RoomSerializer
#     lookup_url_kwarg = "code"

#     def get(self, request, format=None):
#         code = request.GET.get(self.lookup_url_kwarg)

#         if code != None:
#             room = Room.objects.filter(code=code)
#             if len(room) > 0:
#                 data = RoomSerializer(room[0]).data
#                 data["is_host"] = self.request.session.session_key == room[0].host

#                 return Response(data, status=status.HTTP_200_OK)

#             return Response(
#                 {"Room Not Found": "Invalid Room Code."},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         return Response(
#             {"Bad Request": "Code parameter missing."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )


class RoomDetail(APIView):
    serializer_class = RoomSerializer

    def get(self, request, code, format=None):
        room = Room.objects.filter(code=code)
        if len(room) > 0:
            data = RoomSerializer(room[0]).data
            data["is_host"] = self.request.session.session_key == room[0].host

            return Response(data, status=status.HTTP_200_OK)

        return Response(
            {"Room Not Found": "Invalid Room Code."},
            status=status.HTTP_404_NOT_FOUND,
        )


class CreateRoom(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format=None):
        # check if a user is logged in via session
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            guest_can_pause = serializer.data.get("guest_can_pause")
            votes_to_skip = serializer.data.get("votes_to_skip")
            host = self.request.session.session_key

            queryset = Room.objects.filter(host=host)
            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(
                    update_fields=[
                        "guest_can_pause",
                        "votes_to_skip",
                    ]
                )

                self.request.session["room_code"] = room.code

                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

            else:
                room = Room(
                    host=host,
                    guest_can_pause=guest_can_pause,
                    votes_to_skip=votes_to_skip,
                )
                room.save()

                self.request.session["room_code"] = room.code

                return Response(
                    RoomSerializer(room).data, status=status.HTTP_201_CREATED
                )

        return Response(
            {"Bad Request": "Invalid data..."}, status=status.HTTP_400_BAD_REQUEST
        )


class JoinRoom(APIView):
    def post(self, req, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        code = req.data.get("code")

        if code != None:
            queryset = Room.objects.filter(code=code)
            if queryset.exists():
                room = queryset[0]

                self.request.session["room_code"] = room.code

                return Response({"Message": "Room Joined"}, status=status.HTTP_200_OK)

            return Response(
                {"Bad Request": "Room Does Not Exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"Bad Request": "Code Missing from POST Data"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# check if user is 'in a room' by getting its session
class UserInRoom(APIView):
    def get(self, req, format=None):
        # print(f"Request Object: {self.request.__dict__}", file=sys.stderr)
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        data = {"code": self.request.session.get("room_code")}

        return JsonResponse(data, status=status.HTTP_200_OK)


class LeaveRoom(APIView):
    def post(self, req, format=None):
        # if user is 'in room', leave room by removing room_code from its session
        if "room_code" in self.request.session:
            self.request.session.pop("room_code")

            # delete room if user is room host
            host_id = self.request.session.session_key
            queryset = Room.objects.filter(host=host_id)
            if queryset.exists():
                room = queryset[0]
                room.delete()

        return Response({"Message": "Success"}, status=status.HTTP_200_OK)


class UpdateRoom(APIView):
    serializer_class = UpdateRoomSerializer

    def patch(self, req, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serialized_data = self.serializer_class(data=req.data)

        if serialized_data.is_valid():
            code = serialized_data.data.get("code")
            votes = serialized_data.data.get("votes_to_skip")
            can_pause = serialized_data.data.get("guest_can_pause")

            queryset = Room.objects.filter(code=code)
            if queryset.exists():
                room = queryset[0]
                host_id = self.request.session.session_key

                if room.host != host_id:
                    return Response(
                        {"Bad Request": "Permission Denied"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                room.guest_can_pause = can_pause
                room.votes_to_skip = votes

                room.save(update_fields=["guest_can_pause", "votes_to_skip"])
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

            return Response(
                {"Bad Request": "Room Not Found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"Bad Request": "Invalid data..."}, status=status.HTTP_403_FORBIDDEN
        )
