from rest_framework import serializers
from .models import Playlist, Photo, Song, GalleryItem

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'playlist', 'image', 'caption']

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'playlist', 'title', 'file']

class GalleryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryItem
        fields = ['id', 'device_id', 'asset_id', 'file', 'asset_type', 'create_date', 'created_at']

class PlaylistSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = ['id', 'code', 'title', 'dialog', 'photos', 'songs']
