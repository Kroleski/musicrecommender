import datetime
import requests
import numpy as np
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from .forms import TrackSearchForm
from .models import (
    Track, Album, Artist, Image, AvailableMarket, ExternalID,
    SpotifyToken, SavedTrack
)
from .utils.spotify import (
    get_spotify_token, search_tracks, fetch_and_store_track_data
)

def index(request):
    return render(request, 'index.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def spotify_login(request):
    scopes = 'user-library-read playlist-read-private user-read-email'
    redirect_uri = settings.SPOTIFY_REDIRECT_URI
    auth_url = (
        'https://accounts.spotify.com/authorize'
        f'?client_id={settings.SPOTIFY_CLIENT_ID}'
        '&response_type=code'
        f'&redirect_uri={redirect_uri}'
        f'&scope={scopes}'
    )
    print("Spotify auth URL:", auth_url)  # ← Add this for debug
    return redirect(auth_url)

@login_required
def spotify_callback(request):
    code = request.GET.get('code')
    token_url = 'https://accounts.spotify.com/api/token'
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,
    }

    response = requests.post(token_url, data=payload)
    tokens = response.json()

    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    expires_in = tokens.get('expires_in')

    if not access_token:
        return render(request, 'error.html', {'message': 'Spotify authorization failed'})

    expires_at = timezone.now() + datetime.timedelta(seconds=expires_in)
    SpotifyToken.objects.update_or_create(
        user=request.user,
        defaults={
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at,
        }
    )
    return redirect('user_saved_tracks')

@login_required
def user_saved_tracks(request):
    saved_tracks = SavedTrack.objects.filter(user__user=request.user).select_related('track__album').prefetch_related('track__artists')
    return render(request, 'user_saved_tracks.html', {'saved_tracks': saved_tracks})

@login_required
def search_track(request):
    results = []
    if request.method == 'POST':
        form = TrackSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            token = get_spotify_token(request.user)
            results = search_tracks(query, token)
    else:
        form = TrackSearchForm()
    return render(request, 'search.html', {'form': form, 'results': results})

@login_required
def add_track(request):
    if request.method == 'POST':
        track_id = request.POST.get('track_id')
        token = get_spotify_token(request.user)
        fetch_and_store_track_data(track_id, token)
    return redirect('search_track')

@login_required
def track_detail(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    return render(request, 'track_detail.html', {'track': track})

@login_required
def content_based_recommendations(request, track_id):
    target_track = get_object_or_404(Track, id=track_id)
    tracks = Track.objects.exclude(id=track_id)
    features = ['duration_ms', 'popularity']
    track_features = np.array([[getattr(track, feature) or 0 for feature in features] for track in tracks])
    target_features = np.array([[getattr(target_track, feature) or 0 for feature in features]])
    scaler = MinMaxScaler()
    track_features_scaled = scaler.fit_transform(track_features)
    target_features_scaled = scaler.transform(target_features)
    similarities = cosine_similarity(target_features_scaled, track_features_scaled)[0]
    similar_indices = similarities.argsort()[-5:][::-1]
    recommended_tracks = [tracks[i] for i in similar_indices]
    return render(request, 'recommendations.html', {'tracks': recommended_tracks})

@login_required
def fetch_tracks_view(request):
    if request.method == 'POST':
        track_id = request.POST.get('track_id')
        token = get_spotify_token(request.user)
        track = fetch_and_store_track_data(track_id, token)
        if track:
            return redirect('track_detail', track_id=track.id)
        else:
            return render(request, 'error.html', {'message': 'Failed to fetch track data.'})
    return render(request, 'fetch_tracks.html')