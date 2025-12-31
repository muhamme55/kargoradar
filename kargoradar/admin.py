from django.contrib import admin
from .models import DestekMesaji  # modeli içeri aktarmakk için

@admin.register(DestekMesaji)
class DestekMesajiAdmin(admin.ModelAdmin):
    # Panelde hangi sütunların görüneceğini belirliyoruz
    list_display = ('ad_soyad', 'email', 'konu', 'tarih')
    
    # sola tarih filtresi
    list_filter = ('tarih',)
    
    # Arama kutusu ekler 
    search_fields = ('ad_soyad', 'konu', 'email')
    
    readonly_fields = ('tarih',)