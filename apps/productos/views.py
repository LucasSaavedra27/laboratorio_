from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.productos.models import Producto
from apps.productos.forms import FormularioProducto

@login_required
def productos(request):
    productos = Producto.objects.all()  # Obtén todos los productos de la base de datos
    form = FormularioProducto()  # Inicializa el formulario vacío

    if request.method == 'POST':  # Si el formulario fue enviado
        form = FormularioProducto(request.POST)
        if form.is_valid():
            form.save()  # Guarda el nuevo producto en la base de datos
            return redirect('/productos')  # Redirige a la misma página para actualizar la lista de productos

    # Renderiza el template con la lista de productos y el formulario
    return render(request, 'productos/productos.html', {'productos': productos, 'form': form})

def editarProducto(request,producto_id):
    producto = Producto.objects.get(id=producto_id)
    return render(request,'productos/edicionProducto.html',{'producto':producto})

def edicionProducto(request):
    if request.method == 'POST':  
        producto_id = request.POST.get('id')  # Asegúrate de obtener el ID
        producto = Producto.objects.get(id=producto_id)
        producto.nombre = request.POST['nombre']
        producto.precioDeVenta = request.POST['precioDeVenta']
        producto.precioDeCosto = request.POST['precioDeCosto']
        producto.fechaDeElaboracion = request.POST['fechaDeElaboracion']
        producto.fechaDeVencimiento = request.POST['fechaDeVencimiento']
        producto.categoria = request.POST['categoria']
        producto.cantidadDisponible = request.POST['cantidadDisponible']
        producto.cantidadMinRequerida = request.POST['cantidadMinRequerida']
        producto.save()  # Guarda los cambios en la base de datos
        
    return redirect('/productos')  # En caso de que no sea un POST, redirige
    

def eliminarProducto(request,producto_id):
    producto = Producto.objects.get(id=producto_id)
    producto.delete()
    return redirect('/productos')


def buscarProducto(request):
    busqueda = request.POST['busqueda']  # Obtiene el término de búsqueda de la query
    productos = Producto.objects.all()  # Obtiene todos los productos por defecto

    if busqueda:  # Si hay un término de búsqueda
        productos = productos.filter(nombre__icontains=busqueda)  # Filtra los productos por nombre

    return render(request, 'productos/productos.html', {'productos': productos, 'busqueda': busqueda})


