from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_track, name='search_track'),
    path('add/', views.add_track, name='add_track'),
    path('track/<int:track_id>/', views.track_detail, name='track_detail'),
    path('recommendations/<int:track_id>/', views.content_based_recommendations, name='content_based_recommendations'),
    path('fetch/', views.fetch_tracks_view, name='fetch_tracks'),

    # Spotify OAuth login (manual trigger)
    path('spotify/login/', views.spotify_login, name='spotify_login'),
    path('api/callback/', views.spotify_callback, name='spotify_callback'),

    path('dashboard/', views.user_saved_tracks, name='user_saved_tracks'),
]