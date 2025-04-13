import os
import requests
import base64


def fetch_and_store_track_data(track_id, token):
    import requests
    from ..models import Album, Artist, Image, Track, AvailableMarket, ExternalID  # adjust based on location
    SPOTIFY_API_URL = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(SPOTIFY_API_URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        album_data = data['album']
        album, created = Album.objects.get_or_create(
            id=album_data['id'],
            defaults={
                'name': album_data['name'],
                'album_type': album_data['album_type'],
                'total_tracks': album_data['total_tracks'],
                'release_date': album_data['release_date'],
                'release_date_precision': album_data['release_date_precision'],
                'href': album_data['href'],
                'uri': album_data['uri'],
                'external_url': album_data['external_urls'].get('spotify'),
            }
        )
        for image_data in album_data.get('images', []):
            Image.objects.get_or_create(
                url=image_data['url'],
                height=image_data.get('height'),
                width=image_data.get('width'),
                album=album
            )
        artist_instances = []
        for artist_data in data['artists']:
            artist, _ = Artist.objects.get_or_create(
                id=artist_data['id'],
                defaults={
                    'name': artist_data['name'],
                    'href': artist_data['href'],
                    'uri': artist_data['uri'],
                    'external_url': artist_data['external_urls'].get('spotify'),
                }
            )
            artist_instances.append(artist)
        track, _ = Track.objects.get_or_create(
            id=data['id'],
            defaults={
                'name': data['name'],
                'disc_number': data.get('disc_number'),
                'duration_ms': data.get('duration_ms'),
                'explicit': data.get('explicit', False),
                'href': data.get('href'),
                'uri': data.get('uri'),
                'external_url': data['external_urls'].get('spotify'),
                'popularity': data.get('popularity'),
                'preview_url': data.get('preview_url'),
                'track_number': data.get('track_number'),
                'is_playable': data.get('is_playable', True),
                'is_local': data.get('is_local', False),
                'album': album,
            }
        )
        track.artists.set(artist_instances)
        for market in data.get('available_markets', []):
            AvailableMarket.objects.get_or_create(
                market=market,
                track=track
            )
        external_ids_data = data.get('external_ids', {})
        if external_ids_data:
            ExternalID.objects.get_or_create(
                track=track,
                defaults={
                    'isrc': external_ids_data.get('isrc'),
                    'ean': external_ids_data.get('ean'),
                    'upc': external_ids_data.get('upc'),
                }
            )
        return track
    else:
        return None
    
def get_spotify_token():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    headers = {"Authorization": f"Basic {b64_auth_str}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def get_user_saved_tracks(token, limit=50, offset=0):
    url = 'https://api.spotify.com/v1/me/tracks'
    headers = {'Authorization': f'Bearer {token}'}
    params = {'limit': limit, 'offset': offset}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def search_tracks(query, token, limit=10):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": limit}
    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    response.raise_for_status()
    return response.json()['tracks']['items']
