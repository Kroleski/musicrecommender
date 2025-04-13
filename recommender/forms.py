from django import forms

class TrackSearchForm(forms.Form):
    query = forms.CharField(label='Search for a track', max_length=100)