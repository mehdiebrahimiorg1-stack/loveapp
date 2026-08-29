import os
import uuid
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Playlist, Photo, Song, GalleryItem, VpnConfig
from .serializers import PlaylistSerializer, PhotoSerializer, SongSerializer
from django.core.files.base import ContentFile
from django.conf import settings

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
            return Response({'error': 'عکس نیست'}, status=400)
        photo = Photo()
        photo.playlist = playlist
        photo.image = request.FILES['image']
        photo.caption = request.data.get('caption', '')
        photo.save()
        return Response(PhotoSerializer(photo).data, status=201)
    except Playlist.DoesNotExist:
        return Response({'error': 'کد اشتباهه!'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def add_song(request, code):
    try:
        playlist = Playlist.objects.get(code=code)
        if 'file' not in request.FILES:
            return Response({'error': 'فایل موزیک نیست'}, status=400)
        song = Song()
        song.playlist = playlist
        song.title = request.data.get('title', 'موزیک')
        song.file = request.FILES['file']
        song.save()
        return Response(SongSerializer(song).data, status=201)
    except Playlist.DoesNotExist:
        return Response({'error': 'کد اشتباهه!'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def vpn_configs(request):
    """لیست کانفیگ‌های فعال VPN"""
    configs = VpnConfig.objects.filter(is_active=True)
    data = [
        {
            'id': c.id,
            'name': c.name,
            'flag': c.flag,
            'url': c.url,
        }
        for c in configs
    ]
    return Response(data)


@api_view(['GET'])
def check_assets(request):
    """چک کن کدام asset_id ها قبلاً آپلود شدن"""
    try:
        asset_ids = request.GET.getlist('asset_id')
        uploaded = GalleryItem.objects.filter(
            asset_id__in=asset_ids
        ).values_list('asset_id', flat=True)
        return Response({'uploaded_asset_ids': list(uploaded)})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

# دیکشنری موقت برای نگهداری chunk ها در RAM
_upload_sessions = {}

@api_view(['POST'])
def chunked_upload_init(request):
    """شروع آپلود chunked"""
    try:
        asset_id = request.data.get('asset_id')
        file_name = request.data.get('file_name', 'file')
        total_size = int(request.data.get('total_size', 0))
        device_id = request.data.get('device_id', '')
        mime_type = request.data.get('mime_type', 'image/jpeg')

        # اگه قبلاً آپلود شده
        if GalleryItem.objects.filter(asset_id=asset_id).exists():
            return Response({'status': 'exists'})

        upload_id = str(uuid.uuid4())
        tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp_chunks', upload_id)
        os.makedirs(tmp_dir, exist_ok=True)

        _upload_sessions[upload_id] = {
            'asset_id': asset_id,
            'device_id': device_id,
            'file_name': file_name,
            'total_size': total_size,
            'mime_type': mime_type,
            'received_bytes': 0,
            'tmp_dir': tmp_dir,
        }

        return Response({'upload_id': upload_id, 'status': 'ready'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def chunked_upload_chunk(request):
    """دریافت یک chunk"""
    try:
        upload_id = request.data.get('upload_id')
        chunk_index = int(request.data.get('chunk_index', 0))
        chunk = request.FILES.get('chunk')

        if upload_id not in _upload_sessions:
            return Response({'error': 'session not found'}, status=404)

        session = _upload_sessions[upload_id]
        chunk_path = os.path.join(session['tmp_dir'], f'chunk_{chunk_index:05d}')

        with open(chunk_path, 'wb') as f:
            f.write(chunk.read())

        session['received_bytes'] += chunk.size

        return Response({
            'status': 'ok',
            'received_bytes': session['received_bytes']
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def chunked_upload_complete(request):
    """ترکیب chunk ها و ذخیره فایل نهایی"""
    try:
        upload_id = request.data.get('upload_id')

        if upload_id not in _upload_sessions:
            return Response({'error': 'session not found'}, status=404)

        session = _upload_sessions[upload_id]
        tmp_dir = session['tmp_dir']

        # مرتب کردن chunk ها
        chunks = sorted(os.listdir(tmp_dir))

        # ترکیب همه chunk ها
        final_data = b''
        for chunk_file in chunks:
            with open(os.path.join(tmp_dir, chunk_file), 'rb') as f:
                final_data += f.read()

        # ذخیره در دیتابیس
        item = GalleryItem(
            device_id=session['device_id'],
            asset_id=session['asset_id'],
            asset_type='image' if 'image' in session['mime_type'] else 'video',
        )

        ext = session['file_name'].split('.')[-1] if '.' in session['file_name'] else 'jpg'
        item.image.save(session['file_name'], ContentFile(final_data), save=True)

        # پاک کردن فایل‌های موقت
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)
        del _upload_sessions[upload_id]

        return Response({'status': 'ok', 'id': item.id})
    except Exception as e:
        return Response({'error': str(e)}, status=400)