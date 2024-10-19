import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.pedidos.models import Proveedor
from apps.pedidos.forms import FormularioProveedor
from fpdf import FPDF
from django.conf import settings
from datetime import datetime
from django.http import HttpResponse

@login_required
def proveedores(request):
    proveedores = Proveedor.objects.all()
    form = FormularioProveedor()
    mostrar_boton = True # Por defecto, mostramos el botón
    
    if request.method == 'POST':  # Si el formulario fue enviado
        form = FormularioProveedor(request.POST)
        if form.is_valid():
            form.save()  # Guarda el nuevo proveedor en la base de datos
            return redirect('/proveedores') # Redirige a la misma página para actualizar la lista de proveedores
        
    if request.path == '/proveedores/buscar/':
        mostrar_boton = False
        
    return render(request, 'proveedor/proveedores.html', {'proveedores': proveedores, 'form': form,'mostrar_boton': mostrar_boton})

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
        self.cell(w = 0, h = 20, txt = 'Reporte de proveedores', border = 0, ln=1,
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
    pdf.cell(40, 10, "Nombre", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "Apellido", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "DNI", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "Estado", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "Empresa", 1, 1, 'C', fill=True)

    tcol_set(pdf, 'black')
    # Cambiar el estilo de fuente para el contenido
    pdf.set_font("Arial", "", 12)

    # Obtener todos los productos de la base de datos
    proveedores = Proveedor.objects.all()

    # Verificar si hay productos
    if proveedores.exists():
        c = 0  # Contador para alternar el color de las filas
        for proveedor in proveedores:
            c += 1

            # Alternar el color de fondo entre gris y blanco
            if c % 2 == 0:
                bcol_set(pdf, 'gray2')  # Fila gris
            else:
                bcol_set(pdf, 'white')  # Fila blanca
            
            # Dibujar las celdas con el color de fondo establecido
            pdf.cell(40, 10, proveedor.nombre, 1, 0, 'C', fill=True)
            pdf.cell(40, 10, proveedor.apellido, 1, 0, 'C', fill=True)
            pdf.cell(40, 10, proveedor.dni, 1, 0, 'C', fill=True)
            pdf.cell(30, 10, proveedor.estado, 1, 0, 'C', fill=True)
            pdf.cell(40, 10, proveedor.empresa, 1, 1, 'C', fill=True)# Salto de línea entre filas
    else:
        pdf.cell(0, 10, "No hay proveedores disponibles.", 0, 1, 'C')

    # Preparar la respuesta
    response = HttpResponse(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporteProveedores.pdf"'
    return response

