from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def index(request):
    return render(request,'inicio/index.html')

def login_view(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio:index')  
        else:
            error_message = "Nombre de usuario o contraseña incorrectos."
    return render(request, 'registration/login.html', {'error_message': error_message})

def logout_view(request):
    logout(request)
    return redirect('inicio:index') 
