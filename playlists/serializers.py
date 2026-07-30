from rest_framework import serializers
from .models import Playlist, Photo, Song

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'playlist', 'image', 'caption']

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'playlist', 'title', 'file']

class PlaylistSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    songs = SongSerializer(many=True, read_only=True)
    
    class Meta:
        model = Playlist
        fields = ['id', 'code', 'title', 'dialog', 'photos', 'songs']
