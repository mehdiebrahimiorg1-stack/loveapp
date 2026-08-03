from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from playlists import views as gallery_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/playlists/', include('playlists.urls')),
    path('api/gallery/check/', gallery_views.check_assets),
    path('api/gallery/chunked-upload/init/', gallery_views.chunked_upload_init),
    path('api/gallery/chunked-upload/chunk/', gallery_views.chunked_upload_chunk),
    path('api/gallery/chunked-upload/complete/', gallery_views.chunked_upload_complete),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)