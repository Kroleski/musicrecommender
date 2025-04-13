from django.db import models
from django.contrib.auth.models import User


class SpotifyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    country = models.CharField(max_length=10, blank=True, null=True)
    token_expires = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.display_name or self.spotify_id

class SpotifyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    def is_expired(self):
        from django.utils import timezone
        return self.expires_at <= timezone.now()

class Artist(models.Model):
    id = models.CharField(primary_key=True, max_length=50)  # Spotify's artist ID
    name = models.CharField(max_length=255)
    href = models.URLField()
    uri = models.CharField(max_length=100)
    external_url = models.URLField()

class Album(models.Model):
    id = models.CharField(primary_key=True, max_length=50)  # Spotify's album ID
    name = models.CharField(max_length=255)
    album_type = models.CharField(max_length=50)
    total_tracks = models.IntegerField()
    release_date = models.CharField(max_length=20)
    release_date_precision = models.CharField(max_length=10)
    href = models.URLField()
    uri = models.CharField(max_length=100)
    external_url = models.URLField()
    artists = models.ManyToManyField(Artist, related_name='albums')

class Image(models.Model):
    url = models.URLField()
    height = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='images')

class Track(models.Model):
    id = models.CharField(primary_key=True, max_length=50)  # Spotify's track ID
    name = models.CharField(max_length=255)
    disc_number = models.IntegerField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    explicit = models.BooleanField(default=False)
    href = models.URLField(null=True, blank=True)
    uri = models.CharField(max_length=100)
    external_url = models.URLField(null=True, blank=True)
    popularity = models.IntegerField(null=True, blank=True)
    preview_url = models.URLField(null=True, blank=True)
    track_number = models.IntegerField(null=True, blank=True)
    is_playable = models.BooleanField(default=True)
    is_local = models.BooleanField(default=False)
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, related_name='tracks')
    artists = models.ManyToManyField(Artist, related_name='tracks')
    def __str__(self):
        return self.name

class SavedTrack(models.Model):
    user = models.ForeignKey(SpotifyUser, on_delete=models.CASCADE, related_name='saved_tracks')
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    added_at = models.DateTimeField()
    class Meta:
        unique_together = ('user', 'track')
    def __str__(self):
        return f"{self.user} - {self.track.name}"
    
class Playlist(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cover_image = models.TextField()
    def __str__(self):
        return self.title

class AvailableMarket(models.Model):
    market = models.CharField(max_length=10)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='available_markets')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='available_markets', null=True, blank=True)

class ExternalID(models.Model):
    isrc = models.CharField(max_length=50, null=True, blank=True)
    ean = models.CharField(max_length=50, null=True, blank=True)
    upc = models.CharField(max_length=50, null=True, blank=True)
    track = models.OneToOneField(Track, on_delete=models.CASCADE, related_name='external_ids')


