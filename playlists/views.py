from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Playlist, Message
from .serializers import PlaylistSerializer, MessageSerializer

@api_view(['POST'])
def create_playlist(request):
    serializer = PlaylistSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_playlist(request, code):
    try:
        playlist = Playlist.objects.get(code=code)
        serializer = PlaylistSerializer(playlist)
        return Response(serializer.data)
    except Playlist.DoesNotExist:
        return Response({'error': 'کد اشتباهه!'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def add_message(request, code):
    try:
        playlist = Playlist.objects.get(code=code)
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(playlist=playlist)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Playlist.DoesNotExist:
        return Response({'error': 'کد اشتباهه!'}, status=status.HTTP_404_NOT_FOUND)
# Create your views here.
