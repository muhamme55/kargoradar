from django.urls import path
from . import views

app_name = 'kargoyonetim'

urlpatterns = [
    path('sorgula/', views.kargoyonetim, name='locations'),
]