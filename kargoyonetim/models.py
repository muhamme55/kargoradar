from django.db import models
from django.conf import settings  # Kullanıcı modeline erişmek için

class Kargo(models.Model):
    DURUM_CHOICES = [
        ('Hazırlanıyor', 'Hazırlanıyor'),
        ('Yolda', 'Yolda'),
        ('Şubede', 'Şubede'),
        ('Teslim Edildi', 'Teslim Edildi'),
    ]

    tracking_number = models.CharField(max_length=50, unique=True, verbose_name="Takip Numarası")
    
    gonderen = models.CharField(max_length=100, verbose_name="Gönderen Adı")
    gonderen_telefon = models.CharField(max_length=20, blank=True, null=True, verbose_name="Gönderen Telefon")
    gonderen_detay = models.CharField(max_length=200, default="İstanbul / Şişli", verbose_name="Gönderen Şube/Bölge")
    
    alici = models.CharField(max_length=100, verbose_name="Alıcı Adı")
    alici_telefon = models.CharField(max_length=20, blank=True, null=True, verbose_name="Alıcı Telefon")
    
    alici_email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Alıcı E-posta")
    alici_detay = models.CharField(max_length=200, default="Konya / Selçuklu", verbose_name="Alıcı Şube/Bölge")

    gonderi_tarihi = models.DateField(auto_now_add=True, verbose_name="Gönderi Tarihi")
    tarih_string = models.CharField(max_length=20, blank=True, null=True, verbose_name="Görünüm Tarihi (Örn: 19 Ara)")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='Hazırlanıyor', verbose_name="Kargo Durumu")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tracking_number} - {self.alici}"

    class Meta:
        verbose_name = "Kargo"
        verbose_name_plural = "Kargolar"

class KargoTakipLog(models.Model):
    kargo = models.ForeignKey(Kargo, on_delete=models.CASCADE, related_name='hareketler', verbose_name="İlgili Kargo")
    islem_yapan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="İşlemi Yapan Personel")
    eski_durum = models.CharField(max_length=50, null=True, blank=True, verbose_name="Önceki Durum")
    yeni_durum = models.CharField(max_length=50, verbose_name="Yeni Durum")
    aciklama = models.TextField(null=True, blank=True, verbose_name="İşlem Açıklaması")
    tarih = models.DateTimeField(auto_now_add=True, verbose_name="İşlem Tarihi")

    class Meta:
        verbose_name = "Kargo Hareketi"
        verbose_name_plural = "Kargo Hareketleri"
        ordering = ['-tarih'] # En yeni hareketi en üstte gösterir

    def __str__(self):
        return f"{self.kargo.tracking_number} - {self.yeni_durum} ({self.tarih.strftime('%d.%m %H:%M')})"