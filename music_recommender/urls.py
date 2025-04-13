from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from recommender import views as recommender_views

urlpatterns = [
    path('', include('recommender.urls')),
    path('admin/', admin.site.urls),

    # Django built-in login/logout
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Optional signup
    path('signup/', recommender_views.signup_view, name='signup'),
]