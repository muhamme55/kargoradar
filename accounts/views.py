from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout # logout eklendi
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username_girilen = request.POST.get("username")
        password_girilen = request.POST.get("password")

        user = authenticate(request, username=username_girilen, password=password_girilen)

        if user is not None:
            login(request, user)
            messages.success(request, f"Hoş geldiniz, {user.username}!")
            
            if user.is_staff:
                return redirect("kargoekleme:panel_anasayfa")
            else:
                return redirect("home")
        else:
            messages.error(request, "Kullanıcı adı veya şifre hatalı!")

    return render(request, "accounts/login.html")

def logout_view(request):
    """Kullanıcı oturumunu güvenli bir şekilde kapatır."""
    if request.method == "POST":
        logout(request)
        messages.info(request, "Başarıyla çıkış yaptınız.")
        return redirect("home")
    return redirect("home") # GET isteği gelirse de ana sayfaya gönder