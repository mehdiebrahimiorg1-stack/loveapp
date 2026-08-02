from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Playlist, Photo, Song, GalleryItem, ChunkedUpload
from .serializers import PlaylistSerializer, PhotoSerializer, SongSerializer, GalleryItemSerializer
import os, json, uuid, shutil
from django.conf import settings
from django.core.files import File
from django.utils.dateparse import parse_datetime

# ---------- Playlist APIs (بدون تغییر) ----------

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


# ---------- Gallery APIs ----------

@api_view(['POST'])
def upload_gallery(request):
    """این endpoint قدیمیه — فقط برای سازگاری نگه داشته شده"""
    try:
        file = request.FILES.get('file') or request.FILES.get('image')
        device_id = request.POST.get('device_id', '')
        asset_id = request.POST.get('asset_id', '')
        asset_type = request.POST.get('asset_type', 'image')
        create_date = request.POST.get('create_date', None)

        if GalleryItem.objects.filter(asset_id=asset_id).exists():
            return Response({'status': 'exists'})

        item = GalleryItem(
            device_id=device_id,
            asset_id=asset_id,
            asset_type=asset_type,
        )
        if create_date:
            item.create_date = parse_datetime(create_date)
        if file:
            item.file = file
        item.save()
        return Response({'status': 'ok'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
def check_uploaded_assets(request):
    """لیست asset_id هایی که قبلاً آپلود شدن رو برمی‌گردونه"""
    device_id = request.GET.get('device_id', '')
    asset_ids = request.GET.getlist('asset_id')

    queryset = GalleryItem.objects.filter(device_id=device_id)
    if asset_ids:
        queryset = queryset.filter(asset_id__in=asset_ids)

    uploaded = queryset.values_list('asset_id', flat=True)
    return Response({'uploaded_asset_ids': list(uploaded)})


# ---------- Chunked Upload APIs ----------

@api_view(['POST'])
def chunked_upload_init(request):
    """شروع آپلود تکه‌تکه — upload_id می‌سازه"""
    device_id = request.data.get('device_id', '')
    asset_id = request.data.get('asset_id', '')
    file_name = request.data.get('file_name', '')
    total_size = int(request.data.get('total_size', 0))
    mime_type = request.data.get('mime_type', 'image/jpeg')

    # اگه قبلاً کامل آپلود شده
    if GalleryItem.objects.filter(asset_id=asset_id).exists():
        return Response({'status': 'exists'})

    # پاک کردن آپلودهای ناتمام قدیمی همین asset
    ChunkedUpload.objects.filter(asset_id=asset_id, status='pending').delete()

    upload = ChunkedUpload.objects.create(
        device_id=device_id,
        asset_id=asset_id,
        file_name=file_name,
        total_size=total_size,
        chunk_size=1024*1024,  # 1MB
        mime_type=mime_type,
        status='pending'
    )

    # ساخت پوشهٔ موقت
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_chunks', str(upload.upload_id))
    os.makedirs(temp_dir, exist_ok=True)

    return Response({
        'upload_id': str(upload.upload_id),
        'chunk_size': upload.chunk_size,
        'status': 'pending'
    })


@api_view(['POST'])
def chunked_upload_chunk(request):
    """دریافت یک تکه از فایل"""
    upload_id = request.data.get('upload_id')
    chunk_index = int(request.data.get('chunk_index', 0))
    chunk_file = request.FILES.get('chunk')

    if not upload_id or chunk_file is None:
        return Response({'error': 'upload_id و chunk لازمن'}, status=400)

    try:
        upload = ChunkedUpload.objects.get(upload_id=upload_id)
    except ChunkedUpload.DoesNotExist:
        return Response({'error': 'Upload not found'}, status=404)

    if upload.status == 'complete':
        return Response({'status': 'complete', 'received_bytes': upload.total_size})

    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_chunks', str(upload.upload_id))
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, 'upload.tmp')
    meta_file = os.path.join(temp_dir, 'meta.json')

    # نوشتن تکه در جای درست
    mode = 'r+b' if os.path.exists(temp_file) else 'wb'
    with open(temp_file, mode) as f:
        f.seek(chunk_index * upload.chunk_size)
        for chunk in chunk_file.chunks():
            f.write(chunk)

    # ثبت تکه‌های دریافت‌شده
    received_chunks = []
    if os.path.exists(meta_file):
        with open(meta_file, 'r') as f:
            received_chunks = json.load(f)

    if chunk_index not in received_chunks:
        received_chunks.append(chunk_index)
        with open(meta_file, 'w') as f:
            json.dump(received_chunks, f)

    # محاسبهٔ بایت‌های دریافت‌شده
    expected_chunks = (upload.total_size + upload.chunk_size - 1) // upload.chunk_size
    last_chunk_index = expected_chunks - 1
    last_chunk_size = upload.total_size - (last_chunk_index * upload.chunk_size)

    full_chunks = [c for c in received_chunks if c != last_chunk_index]
    received_bytes = len(full_chunks) * upload.chunk_size
    if last_chunk_index in received_chunks:
        received_bytes += last_chunk_size

    upload.received_bytes = received_bytes
    upload.save()

    return Response({
        'status': 'pending',
        'received_bytes': received_bytes,
        'total_size': upload.total_size
    })


@api_view(['POST'])
def chunked_upload_complete(request):
    """پایان آپلود — فایل نهایی ساخته می‌شه"""
    upload_id = request.data.get('upload_id')

    if not upload_id:
        return Response({'error': 'upload_id لازمه'}, status=400)

    try:
        upload = ChunkedUpload.objects.get(upload_id=upload_id)
    except ChunkedUpload.DoesNotExist:
        return Response({'error': 'Upload not found'}, status=404)

    if upload.status == 'complete':
        return Response({'status': 'exists'})

    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_chunks', str(upload.upload_id))
    temp_file = os.path.join(temp_dir, 'upload.tmp')
    meta_file = os.path.join(temp_dir, 'meta.json')

    if not os.path.exists(temp_file):
        return Response({'error': 'هیچ داده‌ای دریافت نشده'}, status=400)

    actual_size = os.path.getsize(temp_file)
    if actual_size != upload.total_size:
        return Response({
            'error': 'Size mismatch',
            'expected': upload.total_size,
            'actual': actual_size
        }, status=400)

    # ساخت GalleryItem
    final_filename = f"{uuid.uuid4().hex}_{upload.file_name}"

    gallery_item = GalleryItem(
        device_id=upload.device_id,
        asset_id=upload.asset_id,
        asset_type='image' if 'image' in upload.mime_type else 'video',
    )

    with open(temp_file, 'rb') as f:
        gallery_item.file.save(final_filename, File(f), save=True)
    gallery_item.save()

    # پاکسازی
    shutil.rmtree(temp_dir, ignore_errors=True)
    upload.status = 'complete'
    upload.save()

    return Response({
        'status': 'ok',
        'gallery_item_id': gallery_item.id
    })
