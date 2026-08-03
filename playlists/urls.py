from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_playlist, name='create_playlist'),
    path('check/', views.check_assets, name='check_assets'),
    path('chunked-upload/init/', views.chunked_upload_init, name='chunked_init'),
    path('chunked-upload/chunk/', views.chunked_upload_chunk, name='chunked_chunk'),
    path('chunked-upload/complete/', views.chunked_upload_complete, name='chunked_complete'),
    path('<str:code>/', views.get_playlist, name='get_playlist'),
    path('<str:code>/add-photo/', views.add_photo, name='add_photo'),
    path('<str:code>/add-song/', views.add_song, name='add_song'),
]