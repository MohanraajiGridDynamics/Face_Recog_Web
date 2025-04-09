from django.urls import path
from . import views

urlpatterns = [
    # path('', views.upload_and_run, name='upload_and_run'),
    path('', views.upload_and_run, name='home'),
    path('video_feed/', views.video_feed, name='video_feed'),
]
