from django.contrib import admin
from .models import Kargo, KargoTakipLog

@admin.register(Kargo)
class KargoAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'alici', 'durum', 'olusturulma_tarihi')
    search_fields = ('tracking_number', 'alici', 'gonderen')
    list_filter = ('durum',)

@admin.register(KargoTakipLog)
class KargoTakipLogAdmin(admin.ModelAdmin):
    list_display = ('kargo', 'islem_yapan', 'eski_durum', 'yeni_durum', 'tarih')
    list_filter = ('yeni_durum', 'tarih')
    search_fields = ('kargo__tracking_number', 'islem_yapan__username')
    readonly_fields = ('tarih',)