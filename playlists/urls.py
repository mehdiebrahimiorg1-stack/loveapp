from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_playlist, name='create_playlist'),
    path('<str:code>/', views.get_playlist, name='get_playlist'),
    path('<str:code>/add-photo/', views.add_photo, name='add_photo'),
    path('<str:code>/add-song/', views.add_song, name='add_song'),
]
