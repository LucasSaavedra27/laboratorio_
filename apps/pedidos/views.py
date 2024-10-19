from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.pedidos.models import Proveedor
from apps.pedidos.forms import FormularioProveedor

# @login_required
def proveedores(request):
    proveedores = Proveedor.objects.all()
    form = FormularioProveedor()
    
    if request.method == 'POST':  # Si el formulario fue enviado
        form = FormularioProveedor(request.POST)
        if form.is_valid():
            form.save()  # Guarda el nuevo proveedor en la base de datos
            return redirect('/proveedores') # Redirige a la misma página para actualizar la lista de proveedores
    return render(request, 'proveedor/proveedores.html', {'proveedores': proveedores, 'form': form})

def editarProveedor(request,proveedor_id): #Pasar el proveedor a la plantilla edicionProveedor
    proveedor = Proveedor.objects.get(id=proveedor_id)
    return render(request,'proveedor/edicionProveedor.html',{'proveedor':proveedor})

def edicionProveedor(request):
    if request.method == 'POST':  
        proveedor_id = request.POST.get('id')  # Asegúrate de obtener el ID
        proveedor = Proveedor.objects.get(id=proveedor_id)
        proveedor.nombre = request.POST['nombre']
        proveedor.apellido = request.POST['apellido']
        proveedor.dni = request.POST['dni']
        proveedor.direccion = request.POST['direccion']
        proveedor.telefono = request.POST['telefono']
        proveedor.mail = request.POST['mail']
        proveedor.estado = request.POST['estado']
        proveedor.empresa = request.POST['empresa']
        proveedor.save()  # Guarda los cambios en la base de datos
        
    return redirect('/proveedores')  # En caso de que no sea un POST, redirige

def eliminarProveedor(request,proveedor_id):
    proveedor = Proveedor.objects.get(id=proveedor_id)
    proveedor.delete()
    return redirect('/proveedores')

# 
def buscarProveedor(request):
    busqueda = request.POST['busqueda']  # Obtiene el término de búsqueda de la query
    proveedor = Proveedor.objects.all()  # Obtiene todos los productos por defecto

    if busqueda:  # Si hay un término de búsqueda
        proveedor = proveedor.filter(dni__icontains=busqueda)  # Filtra los productos por nombre

    return render(request, 'proveedor/proveedores.html', {'proveedores': proveedor, 'busqueda': busqueda})

