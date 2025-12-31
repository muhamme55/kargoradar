import random
import string
import openpyxl
import qrcode
import base64
from io import BytesIO
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from kargoyonetim.models import Kargo, KargoTakipLog 
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader 

def is_sube_muduru(user):
    return user.groups.filter(name='şube müdürü').exists() or user.is_superuser

def is_sube_personeli_veya_ustu(user):
    return user.groups.filter(name__in=['şube personeli', 'şube müdürü']).exists() or user.is_superuser

def is_personel(user):
    return user.groups.filter(name__in=['kurye', 'şube personeli', 'şube müdürü']).exists() or user.is_superuser


@login_required(login_url='accounts:login')
@user_passes_test(is_personel, login_url='home')
def kurumsal_panel(request):
    """Ana dashboard ve kargo listeleme ekranı."""
    query = request.GET.get('q')
    tum_kargolar = Kargo.objects.all()
    
    if query:
        kargolar = tum_kargolar.filter(tracking_number__icontains=query).order_by('-olusturulma_tarihi')
    else:
        kargolar = tum_kargolar.order_by('-olusturulma_tarihi')

    istatistikler = {
        'toplam': tum_kargolar.count(),
        'hazirlaniyor': tum_kargolar.filter(durum='Hazırlanıyor').count(),
        'yolda': tum_kargolar.filter(durum='Yolda').count(),
        'subede': tum_kargolar.filter(durum='Şubede').count(),
        'teslim_edilen': tum_kargolar.filter(durum='Teslim Edildi').count(),
    }
        
    return render(request, 'kargoekleme.html', {
        'kargolar': kargolar, 
        'istatistikler': istatistikler
    })

@login_required(login_url='accounts:login')
@user_passes_test(is_sube_personeli_veya_ustu, login_url='kargoekleme:panel_anasayfa')
def kargo_ekle_sayfasi(request):
    """Yeni kargo oluşturur, e-posta bilgisini alır ve ilk logu atar."""
    if request.method == "POST":
        rastgele_sayilar = ''.join(random.choices(string.digits, k=6))
        takip_no = f"KR{rastgele_sayilar}"

        yeni_kargo = Kargo.objects.create(
            tracking_number=takip_no,
            gonderen=request.POST.get('sender_name'),
            gonderen_telefon=request.POST.get('sender_phone'),
            gonderen_detay=request.POST.get('sender_address'),
            alici=request.POST.get('receiver_name'),
            alici_telefon=request.POST.get('receiver_phone'),
            alici_email=request.POST.get('receiver_email'),
            alici_detay=request.POST.get('receiver_address'),
            tarih_string=timezone.now().strftime("%d %b"),
            durum="Hazırlanıyor" 
        )

        KargoTakipLog.objects.create(
            kargo=yeni_kargo,
            islem_yapan=request.user,
            yeni_durum="Hazırlanıyor",
            aciklama="Yeni kargo kaydı oluşturuldu."
        )

        return redirect('kargoekleme:panel_anasayfa')
    return render(request, 'yeni_kargo.html')

@login_required(login_url='accounts:login')
@user_passes_test(is_personel, login_url='kargoekleme:panel_anasayfa')
def kargo_detay_view(request, kargo_id):
    """Kargo detaylarını gösterir ve güncelleme yapıldığında verileri kaydeder."""
    kargo = get_object_or_404(Kargo, id=kargo_id)
    
    if request.method == "POST":
        if not is_sube_personeli_veya_ustu(request.user):
            return HttpResponseForbidden("Bu bilgileri düzenleme yetkiniz yok.")
            
        kargo.gonderen = request.POST.get('sender_name')
        kargo.gonderen_telefon = request.POST.get('sender_phone')
        kargo.gonderen_detay = request.POST.get('sender_address')
        kargo.alici = request.POST.get('receiver_name')
        kargo.alici_telefon = request.POST.get('receiver_phone')
        kargo.alici_email = request.POST.get('receiver_email')
        kargo.alici_detay = request.POST.get('receiver_address')
        kargo.save()

        KargoTakipLog.objects.create(
            kargo=kargo,
            islem_yapan=request.user,
            yeni_durum=kargo.durum,
            aciklama=f"Kargo detay bilgileri personel tarafından güncellendi."
        )

        return redirect('kargoekleme:panel_anasayfa')
        
    return render(request, 'kargo_detay.html', {'kargo': kargo})

@login_required(login_url='accounts:login')
@user_passes_test(is_personel, login_url='home')
def kargo_durum_guncelle(request, kargo_id):
    """Durum değişikliğini kaydeder ve alıcıya ŞIK HTML e-posta gönderir."""
    if request.method == "POST":
        kargo = get_object_or_404(Kargo, id=kargo_id) 
        eski_durum = kargo.durum
        yeni_durum = request.POST.get('yeni_durum')
        
        if eski_durum != yeni_durum:

            kargo.durum = yeni_durum
            kargo.save()
            
            KargoTakipLog.objects.create(
                kargo=kargo,
                islem_yapan=request.user,
                eski_durum=eski_durum,
                yeni_durum=yeni_durum,
                aciklama=f"Kargo durumu '{yeni_durum}' olarak güncellendi."
            )
            
            if kargo.alici_email:
                subject = f"KargoRadar Bilgilendirme: #{kargo.tracking_number}"
                
                context = {
                    'alici_adi': kargo.alici,
                    'takip_no': kargo.tracking_number,
                    'yeni_durum': yeni_durum,
                }
                
                html_content = render_to_string('kargo_email_sablon.html', context)
                text_content = strip_tags(html_content)

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[kargo.alici_email]
                )
                msg.attach_alternative(html_content, "text/html")
                
                try:
                    msg.send()
                    print(f"Başarılı: Profesyonel mail gönderildi -> {kargo.alici_email}")
                except Exception as e:
                    print(f"Hata: E-posta gönderilemedi -> {e}")
                
    return redirect('kargoekleme:panel_anasayfa')

@login_required(login_url='accounts:login')
@user_passes_test(is_sube_personeli_veya_ustu, login_url='kargoekleme:panel_anasayfa')
def kargo_sil(request, kargo_id):
    kargo = get_object_or_404(Kargo, id=kargo_id)
    if request.method == "POST":
        kargo.delete()
    return redirect('kargoekleme:panel_anasayfa')

@login_required(login_url='accounts:login')
@user_passes_test(is_sube_muduru, login_url='kargoekleme:panel_anasayfa')
def kargo_excel_rapor(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Kargo Listesi"
    ws.append(['Takip No', 'Gönderen', 'Alıcı', 'Alıcı E-posta', 'Durum', 'Kayıt Tarihi'])
    
    for kargo in Kargo.objects.all().order_by('-olusturulma_tarihi'):
        ws.append([
            kargo.tracking_number, 
            kargo.gonderen, 
            kargo.alici, 
            kargo.alici_email if kargo.alici_email else "Belirtilmedi",
            kargo.durum, 
            kargo.olusturulma_tarihi.strftime("%d.%m.%Y %H:%M")
        ])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Kargo_Raporu_{timezone.now().strftime("%d_%m_%Y")}.xlsx'
    wb.save(response)
    return response

@login_required(login_url='accounts:login')
@user_passes_test(is_personel)
def kargo_etiket_pdf(request, kargo_id):
    kargo = get_object_or_404(Kargo, id=kargo_id)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A6)
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(kargo.tracking_number)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_reader = ImageReader(qr_buffer)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(52.5*mm, 140*mm, "KR KARGO") 
    p.line(10*mm, 135*mm, 95*mm, 135*mm)
    p.drawImage(qr_reader, 70*mm, 108*mm, width=25*mm, height=25*mm)
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(10*mm, 122*mm, f"TAKIP NO: {kargo.tracking_number}")
    p.setFont("Helvetica", 10)
    p.drawString(10*mm, 110*mm, f"GONDERICI: {kargo.gonderen}")
    p.line(10*mm, 105*mm, 65*mm, 105*mm)
    
    p.setFont("Helvetica-Bold", 11)
    p.drawString(10*mm, 95*mm, f"ALICI: {kargo.alici}")
    p.setFont("Helvetica", 10)
    p.drawString(10*mm, 88*mm, f"TEL: {kargo.alici_telefon}")
    p.drawString(10*mm, 81*mm, "ADRES:")
    
    p.setFont("Helvetica", 9)
    adres = kargo.alici_detay
    if len(adres) > 45:
        p.drawString(12*mm, 74*mm, f"{adres[:45]}")
        p.drawString(12*mm, 68*mm, f"{adres[45:90]}...")
    else:
        p.drawString(12*mm, 74*mm, f"{adres}")
    
    p.setFont("Helvetica-Oblique", 7)
    p.drawString(10*mm, 5*mm, f"Etiket Tarihi: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')