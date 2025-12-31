from django.urls import path
from . import views

app_name = 'kargoekleme'

urlpatterns = [
    # Ana Panel çağırma
    path('', views.kurumsal_panel, name='panel_anasayfa'),
    
    # Yeni Kargo Ekleme içim
    path('yeni-kargo/', views.kargo_ekle_sayfasi, name='kargo_ekle_sayfasi'),
    
    # Kargo Detay ve Düzenleme
    path('detay/<int:kargo_id>/', views.kargo_detay_view, name='kargo_detay'),
    
    # Hızlı Durum Güncellemek için
    path('durum-guncelle/<int:kargo_id>/', views.kargo_durum_guncelle, name='kargo_durum_guncelle'),
    
    # Kargo Silmek için 
    path('kargo-sil/<int:kargo_id>/', views.kargo_sil, name='kargo_sil'),
    
    # Tüm kargoları Excel olarak indirir
    path('excel-indir/', views.kargo_excel_rapor, name='excel_indir'),
    
    # her kargo için etiket PDF oluşturur
    path('etiket-pdf/<int:kargo_id>/', views.kargo_etiket_pdf, name='etiket_pdf'),
]