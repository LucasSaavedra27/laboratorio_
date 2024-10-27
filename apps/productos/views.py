from datetime import datetime
import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.productos.models import Producto, Insumo
from apps.productos.forms import FormularioProducto, FormularioInsumo
from fpdf import FPDF
from django.conf import settings


@login_required
def productos(request):
    productos = Producto.objects.all()  # Obtén todos los productos de la base de datos
    return render(request, 'productos/productos.html', {'productos': productos})

def agregarProducto(request):
    form = FormularioProducto() 
    if request.method == 'POST':
        form = FormularioProducto(request.POST)
        if form.is_valid():
            form.save()  # 
            return redirect('/productos')  
    return render(request, 'productos/agregarProducto.html', {'form': form})

def editarProducto(request,producto_id):
    producto = Producto.objects.get(id=producto_id)
    return render(request,'productos/edicionProducto.html',{'producto':producto})

def edicionProducto(request):
    if request.method == 'POST':  
        producto_id = request.POST.get('id')
        producto = Producto.objects.get(id=producto_id)
        producto.nombre = request.POST['nombre']
        producto.precioDeVenta = request.POST['precioDeVenta']
        producto.precioDeCosto = request.POST['precioDeCosto']
        producto.fechaDeElaboracion = request.POST['fechaDeElaboracion']
        producto.fechaDeVencimiento = request.POST['fechaDeVencimiento']
        producto.categoria = request.POST['categoria']
        producto.unidadDeMedida = request.POST['unidadDeMedida']
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

def diccionario_colores(color): 
    colores = {
        'black' : (0,0,0), 
        'white' : (255,255,255),
        'green' : (96,218,117),
        'blue' : (96,181,218),
        'red': (119,30,48),
        'rose':(214,74,236),
        'gray':(103,103,103),
        'gray2':(233,233,233),
        }

    return colores[color]

def dcol_set(hoja, color):
    cr, cg, cb = diccionario_colores(color)
    hoja.set_draw_color(r= cr, g = cg, b= cb)

def bcol_set(hoja,color):
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
        
        # Verificar si el archivo existe
        if os.path.exists(logo):
            self.image(logo, x=10, y=10, w=30, h=30) 
        
        self.set_font('Arial', '', 15)

        tcol_set(self, 'red')
        tfont_size(self,30)
        tfont(self,'B')
        self.cell(w = 0, h = 20, txt = 'Reporte de productos', border = 0, ln=1,
                align = 'C', fill = 0)

        tfont_size(self,10)
        tcol_set(self, 'black')
        tfont(self,'I')
        self.cell(w = 0, h = 10, txt = f'Generado el {datetime.now().strftime("%d/%m/%y")}', border = 0, ln=2,
                align = 'C', fill = 0)

        self.ln(5)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-20)

        # Arial italic 8
        self.set_font('Arial', 'I', 12)

        # Page number
        self.cell(w = 0, h = 10, txt =  'Pagina ' + str(self.page_no()),
                 border = 0,
                align = 'C', fill = 0)

def generarPDF(request):
    # Crear un objeto FPDF
    pdf = PDF()
    pdf.add_page()
    
    # Configuración de la tabla
    # Cambiar el color del fondo a verde para los títulos de la tabla
    bcol_set(pdf, 'red')  # Establece el color verde para el fondo de las celdas
    tcol_set(pdf, 'white')
    pdf.set_font("Arial", "B", 12)

    # Dibujar las celdas de los títulos con fondo verde
    pdf.cell(50, 10, "Nombre", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "Precio", 1, 0, 'C', fill=True)
    pdf.cell(50, 10, "Cantidad Disponible", 1, 0, 'C', fill=True)
    pdf.cell(50, 10, "Fecha de vencimiento", 1, 1, 'C', fill=True)

    tcol_set(pdf, 'black')
    # Cambiar el estilo de fuente para el contenido
    pdf.set_font("Arial", "", 12)

    # Obtener todos los productos de la base de datos
    productos = Producto.objects.all()

    # Verificar si hay productos
    if productos.exists():
        c = 0  # Contador para alternar el color de las filas
        for producto in productos:
            c += 1

            # Alternar el color de fondo entre gris y blanco
            if c % 2 == 0:
                bcol_set(pdf, 'gray2')  # Fila gris
            else:
                bcol_set(pdf, 'white')  # Fila blanca
            
            # Dibujar las celdas con el color de fondo establecido
            pdf.cell(50, 10, producto.nombre, 1, 0, 'C', fill=True)
            pdf.cell(40, 10, f"${producto.precioDeVenta:.2f}", 1, 0, 'C', fill=True)
            pdf.cell(50, 10, f"{producto.cantidadDisponible}", 1, 0, 'C', fill=True)
            pdf.cell(50, 10, f"{producto.fechaDeVencimiento}", 1, 1, 'C', fill=True)  # Salto de línea entre filas
    else:
        pdf.cell(0, 10, "No hay productos disponibles.", 0, 1, 'C')

    # Preparar la respuesta
    response = HttpResponse(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporteProductos.pdf"'
    return response


#-------------------------------------INSUMOS----------------------------------------------------------

def insumos(request):
    insumos = Insumo.objects.all()  # Obtén todos los insumos de la base de datos
    form = FormularioInsumo()
    mostrar_boton = True
    
    if request.method == 'POST':  # Si el formulario fue enviado
        form = FormularioInsumo(request.POST)
        if form.is_valid():
            form.save()  # Guarda el nuevo insumo en la base de datos
            return redirect('/productos/insumos') # Redirige a la misma página para actualizar la lista de insumos
    
    if request.path == '/proveedores/buscar/':
        mostrar_boton = False
        
    return render(request, 'insumos/insumos.html', {'insumos': insumos, 'form': form,'mostrar_boton': mostrar_boton})

def editarInsumo(request,insumo_id): #Pasar el insumo a la plantilla edicionInsumo
    insumo = Insumo.objects.get(id=insumo_id)
    return render(request,'insumos/edicionInsumo.html',{'insumo':insumo})

def edicionInsumo(request):
    if request.method == 'POST':  
        insumo_id = request.POST.get('id')  # Asegúrate de obtener el ID
        insumo = Insumo.objects.get(id=insumo_id)
        insumo.nombre = request.POST['nombre']
        insumo.unidadDeMedida = request.POST['unidadDeMedida']
        insumo.cantidadDisponible = request.POST['cantidadDisponible']
        insumo.cantidadMinRequerida = request.POST['cantidadMinRequerida']
        insumo.precioInsumo = request.POST['precioInsumo']
        insumo.save()  # Guarda los cambios en la base de datos
        
    return redirect('/productos/insumos')  # En caso de que no sea un POST, redirige

def eliminarInsumo(request,insumo_id):
    insumo = Insumo.objects.get(id=insumo_id)
    insumo.delete()
    return redirect('/productos/insumos')

def buscarInsumo(request):
    busqueda = request.POST['busqueda']  # Obtiene el término de búsqueda de la query
    insumo = Insumo.objects.all()  # Obtiene todos los insumos por defecto

    if busqueda:  # Si hay un término de búsqueda
        insumo = insumo.filter(nombre__icontains=busqueda)  # Filtra los insumo por nombre

    return render(request, 'insumos/insumos.html', {'insumos': insumo, 'busqueda': busqueda})

class PDFInsumos(FPDF):
    def header(self):
        logo = os.path.join(settings.BASE_DIR, 'static', 'img', 'logotipo.png')
        
        # Verificar si el archivo existe
        if os.path.exists(logo):
            self.image(logo, x=10, y=10, w=30, h=30) 
        
        self.set_font('Arial', '', 15)

        tcol_set(self, 'red')
        tfont_size(self,30)
        tfont(self,'B')
        self.cell(w = 0, h = 10, txt = 'Reporte de', border = 0, ln=1,
                align = 'C', fill = 0)
        self.cell(w = 0, h = 10, txt = 'Insumos Faltantes', border = 0, align = 'C', ln=1, fill = 0)

        tfont_size(self,10)
        tcol_set(self, 'black')
        tfont(self,'I')
        self.cell(w = 0, h = 10, txt = f'Generado el {datetime.now().strftime("%d/%m/%y")}', border = 0, ln=2,
                align = 'C', fill = 0)

        self.ln(5)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-20)

        # Arial italic 8
        self.set_font('Arial', 'I', 12)

        # Page number
        self.cell(w = 0, h = 10, txt =  'Pagina ' + str(self.page_no()),
                 border = 0,
                align = 'C', fill = 0)

def generarPDFInsumoFaltante(request):
    # Crear un objeto FPDF
    pdf = PDFInsumos()
    pdf.add_page()
    
    # Configuración de la tabla
    # Cambiar el color del fondo a verde para los títulos de la tabla
    bcol_set(pdf, 'red')  # Establece el color verde para el fondo de las celdas
    tcol_set(pdf, 'white')
    pdf.set_font("Arial", "B", 12)

    # Dibujar las celdas de los títulos con fondo verde
    pdf.cell(50, 10, "Nombre", 1, 0, 'C', fill=True)
    pdf.cell(50, 10, "Cantidad Disponible", 1, 0, 'C', fill=True)
    pdf.cell(50, 10, "Cantidad Requerida", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "Precio", 1, 1, 'C', fill=True)

    tcol_set(pdf, 'black')
    # Cambiar el estilo de fuente para el contenido
    pdf.set_font("Arial", "", 12)

    # Obtener todos los productos de la base de datos
    insumos = Insumo.objects.all()

    # Verificar si hay productos
    if insumos.exists():
        c = 0  # Contador para alternar el color de las filas
        for insumo in insumos:
            if insumo.cantidadDisponible < insumo.cantidadMinRequerida:
                c += 1

                # Alternar el color de fondo entre gris y blanco
                if c % 2 == 0:
                    bcol_set(pdf, 'gray2')  # Fila gris
                else:
                    bcol_set(pdf, 'white')  # Fila blanca
                
                # Dibujar las celdas con el color de fondo establecido
                pdf.cell(50, 10, insumo.nombre, 1, 0, 'C', fill=True)
                pdf.cell(50, 10, str(insumo.cantidadDisponible), 1, 0, 'C', fill=True)
                pdf.cell(50, 10, str(insumo.cantidadMinRequerida), 1, 0, 'C', fill=True)
                pdf.cell(40, 10, str(insumo.precioInsumo), 1, 1, 'C', fill=True)  # Salto de línea entre filas
    else:
        pdf.cell(0, 10, "No hay insumos disponibles.", 0, 1, 'C')

    # Preparar la respuesta
    response = HttpResponse(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporteInsumosFaltantes.pdf"'
    return response