from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages 
from .models import DestekMesaji

# --- E-POSTA İÇİN GEREKLİ KÜTÜPHANELER ---
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def home(request):
    return render(request, "base.html")

def tracking(request):
    return HttpResponse("Gönderi Takibi Sayfası (tracking)")

def locations(request):
    if request.method == "POST":
        tracking_number = request.POST.get("tracking_number")
        return HttpResponse(f"Takip Ediliyor: {tracking_number}")
    return HttpResponse("Takip Formuna POST ile gönderi yapılmalı.")

def help(request):
    return HttpResponse("Yardım Sayfası (help)")

def about(request):
    return render(request, "about.html")

def konum(request):
    return render(request, "konum.html")

def isletme(request):
    return render(request, "isletme.html")

def support(request):
    if request.method == "POST":
        # 1. Formdan verileri alıyoruz
        ad = request.POST.get('name') 
        email = request.POST.get('email')
        konu_basligi = request.POST.get('subject')
        mesaj_icerigi = request.POST.get('message')

        # 2. Veritabanına kaydediyoruz (Admin panelinde görünmesi için)
        DestekMesaji.objects.create(
            ad_soyad=ad,
            email=email,
            konu=konu_basligi,
            mesaj=mesaj_icerigi
        )

        # 3. E-posta gönderme işlemi
        admin_alici = "radarkargo5@gmail.com"  # Bildirimin gideceği adres
        mail_konusu = f"Yeni Destek Bildirimi: {konu_basligi}"
        
        # HTML mail içeriği için verileri hazırlıyoruz
        context = {
            'ad': ad,
            'email': email,
            'konu_basligi': konu_basligi,
            'mesaj_icerigi': mesaj_icerigi,
        }
        
        # destek_bildirim.html şablonunu kullanıyoruz
        html_icerik = render_to_string('destek_bildirim.html', context)
        duz_metin = strip_tags(html_icerik) # HTML açamayan mailler için

        msg = EmailMultiAlternatives(
            subject=mail_konusu,
            body=duz_metin,
            from_email=settings.EMAIL_HOST_USER, # settings.py'deki mail adresiniz
            to=[admin_alici]
        )
        msg.attach_alternative(html_icerik, "text/html")

        try:
            msg.send()
            messages.success(request, "Mesajınız başarıyla iletildi! Ekibimize e-posta ile ulaştı.")
        except Exception as e:
            # E-posta gitmezse bile veritabanına kaydedildiği için başarı mesajı verebiliriz
            # ya da terminalde hatayı görmek için print edebiliriz.
            print(f"Mail Hatası: {e}")
            messages.success(request, "Mesajınız kaydedildi. Teşekkür ederiz.")

        return redirect('support')
    
    return render(request, "support.html")

def kargoekle(request):
    return render(request, "kargoekleme.html")

def delivery_help(request):
    return HttpResponse("Teslimat Yardımı Sayfası (delivery_help)")