from django.shortcuts import render, redirect
from .models import Kargo 

def kargoyonetim(request):
    """Kullanıcının anasayfadan yaptığı takip sorgusunu işler"""
    
    if request.method == "POST":
        raw_takip_no = request.POST.get('tracking_number', '')
        takip_no = raw_takip_no.strip()
        
        if not takip_no:
            return redirect('home')
            
        kargo = Kargo.objects.filter(tracking_number=takip_no).first()
        
        if kargo:
            return render(request, 'kargoyonetim/location.html', {'kargo': kargo})
        else:
            return render(request, 'kargoyonetim/location.html', {
                'hata': f"'{takip_no}' numaralı gönderi sistemimizde kayıtlı değil. Lütfen numaranın doğruluğundan emin olun."
            })
    
    return redirect('home')