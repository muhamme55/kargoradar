from django.db import models

class DestekMesaji(models.Model):
    ad_soyad = models.CharField(max_length=100, verbose_name="Ad Soyad")
    email = models.EmailField(verbose_name="E-posta Adresi")
    konu = models.CharField(max_length=200, verbose_name="Konu")
    mesaj = models.TextField(verbose_name="Mesaj")
    tarih = models.DateTimeField(auto_now_add=True, verbose_name="Gönderilme Tarihi")

    def __str__(self):
        return f"{self.ad_soyad} - {self.konu}"

    class Meta:
        verbose_name = "Destek Mesajı"
        verbose_name_plural = "Destek Mesajları"
        ordering = ['-tarih']