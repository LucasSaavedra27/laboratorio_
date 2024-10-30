from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from apps.ventas.models import Venta,DetalleVenta
from apps.ventas.forms import FormularioVenta,DetalleVentaFormSet
from apps.usuarios.models import Empleado
from fpdf import FPDF
from datetime import datetime
import os
from django.http import HttpResponse,JsonResponse
from apps.productos.models import Producto

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
    

from django.shortcuts import render
from .models import ClienteMayorista, Venta

def buscarVentas(request):
    ventas = Venta.objects.all()
    fecha_inicio = request.POST.get('fecha_inicio')
    fecha_fin = request.POST.get('fecha_fin')

    # Lógica de filtrado
    if fecha_inicio and fecha_fin:
        # Filtra por rango de fechas
        ventas = ventas.filter(fechaDeVenta__range=[fecha_inicio, fecha_fin])
    elif fecha_inicio:
        # Si solo se ingresa fecha de inicio, filtra por esa fecha exacta
        ventas = ventas.filter(fechaDeVenta=fecha_inicio)
    else:
        return redirect('/ventas')

    return render(request, 'ventas/ventas.html', {'ventas': ventas, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin})



def diccionario_colores(color): 
    colores = {
        'black' : (0,0,0), 
        'white' : (255,255,255),
        'green' : (96,218,117),
        'blue' : (96,181,218),
        'red': (119,30,48),
        'rose': (214,74,236),
        'gray': (103,103,103),
        'gray2': (233,233,233),
    }
    return colores[color]

def dcol_set(hoja, color):
    cr, cg, cb = diccionario_colores(color)
    hoja.set_draw_color(r= cr, g = cg, b= cb)

def bcol_set(hoja, color):
    cr, cg, cb = diccionario_colores(color)
    hoja.set_fill_color(r= cr, g = cg, b= cb)

def tcol_set(hoja, color):
    cr, cg, cb = diccionario_colores(color)
    hoja.set_text_color(r= cr, g = cg, b= cb)

def tfont_size(hoja, size):
    hoja.set_font_size(size)

def tfont(hoja, estilo, fuente='Arial'):
    hoja.set_font(fuente, style=estilo)

class PDF(FPDF):
    def header(self):
        logo = os.path.join(settings.BASE_DIR, 'static', 'img', 'logotipo.png')
        
        if os.path.exists(logo):
            self.image(logo, x=10, y=10, w=30, h=30) 
        
        self.set_font('Arial', '', 15)
        tcol_set(self, 'red')
        tfont_size(self, 30)
        tfont(self, 'B')
        self.cell(w=0, h=20, txt='Reporte de ventas', border=0, ln=1, align='C', fill=0)

        tfont_size(self, 10)
        tcol_set(self, 'black')
        tfont(self, 'I')
        self.cell(w=0, h=10, txt=f'Generado el {datetime.now().strftime("%d/%m/%y")}', border=0, ln=2, align='C', fill=0)

        self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font('Arial', 'I', 12)
        self.cell(w=0, h=10, txt='Pagina ' + str(self.page_no()), border=0, align='C', fill=0)

def exportarPDF(request):
    pdf = PDF()
    pdf.add_page()
    
    # Configuración de la tabla
    bcol_set(pdf, 'red')  # Fondo rojo para los títulos de la tabla
    tcol_set(pdf, 'white')
    pdf.set_font("Arial", "B", 12)

    # Dibujar las celdas de los títulos con fondo rojo
    pdf.cell(35, 10, "Fecha de Venta", 1, 0, 'C', fill=True)
    pdf.cell(35, 10, "Forma de pago", 1, 0, 'C', fill=True)
    pdf.cell(25, 10, "Factura", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "Cliente", 1, 0, 'C', fill=True)
    pdf.cell(25, 10, "Total", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "Empleado", 1, 1, 'C', fill=True)

    tcol_set(pdf, 'black')
    pdf.set_font("Arial", "", 12)

    ventas = Venta.objects.all()

    if ventas.exists():
        c = 0  # Contador para alternar el color de las filas
        for venta in ventas:
            c += 1

            # Alternar el color de fondo entre gris y blanco
            if c % 2 == 0:
                bcol_set(pdf, 'gray2')  # Fila gris
            else:
                bcol_set(pdf, 'white')  # Fila blanca
            
            # Dibujar las celdas con el color de fondo establecido
            fechaVenta = venta.fechaDeVenta.strftime('%Y-%m-%d')
            pdf.cell(35, 10, fechaVenta, 1, 0, 'C', fill=True)
            pdf.cell(35, 10, f"{venta.formaDePago}", 1, 0, 'C', fill=True)  # Sin `.2f`
            pdf.cell(25, 10, f"{venta.tipoDeComprobante}", 1, 0, 'C', fill=True)
            if venta.clienteMayorista is None:
               pdf.cell(40, 10, "Consumidor Final", 1, 0, 'C', fill=True)
            else:
                pdf.cell(40, 10, f"{venta.clienteMayorista.cuil}", 1, 0, 'C', fill=True)
            pdf.cell(25, 10, f"${venta.total:.2f}", 1, 0, 'C', fill=True)  # Con `.2f` para el total decimal
            pdf.cell(30, 10, f"{venta.empleado.dni}", 1, 1, 'C', fill=True)
    else:
        pdf.cell(0, 10, "No hay productos disponibles.", 0, 1, 'C')

    response = HttpResponse(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporteProductos.pdf"'
    return response

def obtener_precio_producto(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)
        return JsonResponse({'precio': str(producto.precioDeVenta)})
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)