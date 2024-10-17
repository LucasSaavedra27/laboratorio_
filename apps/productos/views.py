from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.productos.models import Producto

@login_required
def productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/productos.html', {'productos': productos})