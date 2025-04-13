from django.contrib import admin
from .models import Artist, Album, Image, Track, Playlist, AvailableMarket, ExternalID


admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Image)
admin.site.register(Track)
admin.site.register(Playlist)
admin.site.register(AvailableMarket)
admin.site.register(ExternalID)