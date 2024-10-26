from django import forms
from django.shortcuts import redirect, render, get_object_or_404

from apps.ventas.models import Venta,DetalleVenta
from apps.ventas.forms import FormularioVenta,DetalleVentaFormSet
from apps.usuarios.models import Empleado

def ventas(request):
    ventas = Venta.objects.all()
    return render(request,'ventas/ventas.html',{'ventas':ventas})

def agregarVenta(request):
    if request.method == 'POST':
        ventaForm = FormularioVenta(request.POST)
        detalleVentaFormset = DetalleVentaFormSet(request.POST)
        
        if ventaForm.is_valid() and detalleVentaFormset.is_valid():

            empleado = get_object_or_404(Empleado, user=request.user)
            venta = ventaForm.save(commit=False)  # No guardar todavía la venta
            venta.empleado = empleado  
            venta.save()  
            totalVenta = 0
            detalles = detalleVentaFormset.save(commit=False) # No guardar todavía los detalles
            
            for detalle in detalles: 
                detalle.venta = venta
                detalle.subTotal = detalle.cantidad * detalle.producto.precioDeVenta
                totalVenta += detalle.subTotal
                producto = detalle.producto
                producto.cantidadDisponible -= detalle.cantidad
                producto.save() #acá vamos a actualizar la cantidad disponible de cada producto cuando se realice una venta
                detalle.save()  #acá guardamos cada detalle de venta
            
            venta.total = totalVenta
            venta.save() #acá se actualiza la venta con todos los detalles de venta y se actualiza el precio total de la venta
            return redirect('/ventas')
    else:
        ventaForm = FormularioVenta()
        detalleVentaFormset = DetalleVentaFormSet()

    return render(request, 'ventas/agregarVenta.html', {'ventaForm': ventaForm,'detalleVentaFormset': detalleVentaFormset,})


def verDetallesVenta(request,venta_id):
    detallesVenta = DetalleVenta.objects.filter(venta_id=venta_id)
    venta = Venta.objects.get(id=venta_id)
    return render(request,'ventas/verDetallesVenta.html',{'detallesVenta':detallesVenta,'venta_id':venta_id,'venta':venta})
    
    
    
    