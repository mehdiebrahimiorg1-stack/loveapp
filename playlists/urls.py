from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_playlist, name='create_playlist'),
    path('gallery-upload/', views.upload_gallery, name='upload_gallery'),
    path('gallery/check/', views.check_uploaded_assets, name='check_uploaded_assets'),
    path('chunked-upload/init/', views.chunked_upload_init, name='chunked_upload_init'),
    path('chunked-upload/chunk/', views.chunked_upload_chunk, name='chunked_upload_chunk'),
    path('chunked-upload/complete/', views.chunked_upload_complete, name='chunked_upload_complete'),
    path('<str:code>/', views.get_playlist, name='get_playlist'),
    path('<str:code>/add-photo/', views.add_photo, name='add_photo'),
    path('<str:code>/add-song/', views.add_song, name='add_song'),
]
