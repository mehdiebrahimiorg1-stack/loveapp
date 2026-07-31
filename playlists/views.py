from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Playlist, Photo, Song
from .serializers import PlaylistSerializer, PhotoSerializer, SongSerializer

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
def add_photo(request, code):
    try:
        playlist = Playlist.objects.get(code=code)
        
        if 'image' not in request.FILES:
            return Response({'error': 'عکس نیست'}, status=status.HTTP_400_BAD_REQUEST)
        
        photo = Photo()
        photo.playlist = playlist
        photo.image = request.FILES['image']
        photo.caption = request.data.get('caption', '')
        photo.save()
        
        serializer = PhotoSerializer(photo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Playlist.DoesNotExist:
        return Response({'error': 'کد اشتباهه!'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def add_song(request, code):
    try:
        playlist = Playlist.objects.get(code=code)
        
        if 'file' not in request.FILES:
            return Response({'error': 'فایل موزیک نیست'}, status=status.HTTP_400_BAD_REQUEST)
        
        song = Song()
        song.playlist = playlist
        song.title = request.data.get('title', 'موزیک')
        song.file = request.FILES['file']
        song.save()
        
        serializer = SongSerializer(song)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Playlist.DoesNotExist:
        return Response({'error': 'کد اشتباهه!'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
