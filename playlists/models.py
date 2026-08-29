from django.db import models
import random, string, uuid, os
from django.conf import settings

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

class Playlist(models.Model):
    code = models.CharField(max_length=6, unique=True, default=generate_code)
    title = models.CharField(max_length=100)
    dialog = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.code})"

class Photo(models.Model):
    playlist = models.ForeignKey(Playlist, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/')
    caption = models.CharField(max_length=200, blank=True)

class Song(models.Model):
    playlist = models.ForeignKey(Playlist, related_name='songs', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to='songs/', blank=True, null=True)

class GalleryItem(models.Model):
    device_id = models.CharField(max_length=200)
    asset_id = models.CharField(max_length=200, unique=True)
    file = models.FileField(upload_to='gallery/')  # برای عکس و ویدیو
    asset_type = models.CharField(max_length=20, default='image')  # image یا video
    create_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_id} - {self.asset_id}"

class VpnConfig(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام سرور')
    flag = models.CharField(max_length=10, default='🌐', verbose_name='پرچم')
    url = models.TextField(verbose_name='کانفیگ URL (vless:// یا vmess://)')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'کانفیگ VPN'
        verbose_name_plural = 'کانفیگ‌های VPN'

    def __str__(self):
        return f"{self.flag} {self.name} ({'فعال' if self.is_active else 'غیرفعال'})"


class ChunkedUpload(models.Model):
    upload_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_id = models.CharField(max_length=200, db_index=True)
    device_id = models.CharField(max_length=200)
    file_name = models.CharField(max_length=255)
    total_size = models.BigIntegerField()
    chunk_size = models.IntegerField(default=1024*1024)  # 1MB
    received_bytes = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, default='pending')  # pending, complete, failed
    mime_type = models.CharField(max_length=100, default='image/jpeg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset_id} - {self.status}"
