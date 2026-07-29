from django.db import models

import random, string

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

class Playlist(models.Model):
    code = models.CharField(max_length=6, unique=True, default=generate_code)
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.code})"

class Message(models.Model):
    playlist = models.ForeignKey(Playlist, related_name='messages', on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    song_title = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
# Create your models here.
