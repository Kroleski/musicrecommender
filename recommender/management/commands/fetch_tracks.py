from django.core.management.base import BaseCommand
from recommender.utils.spotify import get_spotify_token, search_tracks
from recommender.models import Track

class Command(BaseCommand):
    help = 'Fetch tracks from Spotify and store them in the database'

    def handle(self, *args, **kwargs):
        token = get_spotify_token()
        query = "genre:pop"  # Modify this query as needed
        tracks = search_tracks(query, token, limit=20)

        for item in tracks:
            track, created = Track.objects.get_or_create(
                uri=item['uri'],
                defaults={
                    'name': item['name'],
                    'artist': ', '.join(artist['name'] for artist in item['artists']),
                    'popularity': item['popularity'],
                    'playlist': None  # Assign to a playlist if applicable
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added track: {track.name}"))
            else:
                self.stdout.write(f"Track already exists: {track.name}")
