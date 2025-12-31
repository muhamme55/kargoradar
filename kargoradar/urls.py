from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    path('kargoyonetim/', include('kargoyonetim.urls', namespace='kargoyonetim')),
    path('kargoekleme/', include('kargoekleme.urls', namespace='kargoekleme')),
    path("accounts/", include("accounts.urls")),

    path("about/", views.about, name="about"),
    path("support/", views.support, name="support"),
    path("konum/", views.konum, name="konum"),
    path("isletme/", views.isletme, name="isletme"),
    path('help/', views.help, name='help'),
    path('delivery-help/', views.delivery_help, name='delivery_help'),
    
    path('admin/', admin.site.urls),
]