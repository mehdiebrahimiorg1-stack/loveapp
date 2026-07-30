from django.db import models
import random, string

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

class Playlist(models.Model):
    code = models.CharField(max_length=6, unique=True, default=generate_code)
    title = models.CharField(max_length=100)
    dialog = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.title} ({self.code})"

class Photo(models.Model):
    playlist = models.ForeignKey(Playlist, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/')
    caption = models.CharField(max_length=200, blank=True)

class Song(models.Model):
    playlist = models.ForeignKey(Playlist, related_name='songs', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='songs/', blank=True, null=True)



# Create your models here.
