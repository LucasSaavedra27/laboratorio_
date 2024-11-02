from django.shortcuts import redirect, render
from apps.ventas.forms import FormularioMayorista
from apps.ventas.models import ClienteMayorista
from fpdf import FPDF
from datetime import datetime
import os
from django.http import HttpResponse
from django.conf import settings


def listadoMayoristas(request):
    clientes = ClienteMayorista.objects.all()
    return render(request,'clientes/listadoMayoristas.html',{'clientes':clientes})

def agregarMayorista(request):
    form = FormularioMayorista() 
    if request.method == 'POST':
        form = FormularioMayorista(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('/ventas/listadoMayoristas')  
    return render(request, 'clientes/agregarMayorista.html', {'form': form})
    
def editarMayorista(request,mayorista_id):
    cliente = ClienteMayorista.objects.get(id=mayorista_id)
    return render(request,'clientes/edicionMayorista.html',{'cliente':cliente})

def edicionMayorista(request):
    if request.method == 'POST':
        cliente_id=request.POST.get('id') 
        cliente = ClienteMayorista.objects.get(id=cliente_id)
        cliente.nombre=request.POST['nombre']
        cliente.apellido=request.POST['apellido']
        cliente.cuil=request.POST['cuil']
        cliente.direccion=request.POST['direccion']
        cliente.telefono=request.POST['telefono']
        cliente.mail=request.POST['mail']
        cliente.save()
    return redirect('/ventas/listadoMayoristas')
    
def buscarMayorista(request):
    busqueda = request.POST['busqueda'] 
    mayoristas = ClienteMayorista.objects.all() 

    if busqueda:  
        clientes = mayoristas.filter(cuil__icontains=busqueda) 
    else:
        return redirect('/ventas/listadoMayoristas')

    return render(request, 'clientes/listadoMayoristas.html', {'clientes': clientes, 'busqueda': busqueda})

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
        self.cell(w=0, h=20, txt='Reporte de Mayoristas', border=0, ln=1, align='C', fill=0)

        tfont_size(self, 10)
        tcol_set(self, 'black')
        tfont(self, 'I')
        self.cell(w=0, h=10, txt=f'Generado el {datetime.now().strftime("%d/%m/%y")}', border=0, ln=2, align='C', fill=0)

        self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font('Arial', 'I', 12)
        self.cell(w=0, h=10, txt='Pagina ' + str(self.page_no()), border=0, align='C', fill=0)

def exportarPDF_Mayoristas(request):
    pdf = PDF()
    pdf.add_page()
    
    # Configuración de la tabla
    bcol_set(pdf, 'red')  # Fondo rojo para los títulos de la tabla
    tcol_set(pdf, 'white')
    pdf.set_font("Arial", "B", 12)

    # Dibujar las celdas de los títulos con fondo rojo
    pdf.cell(30, 10, "Nombre", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "Apellido", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "CUIL", 1, 0, 'C', fill=True)
    pdf.cell(50, 10, "Dirección", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "Teléfono", 1, 1, 'C', fill=True) 

    tcol_set(pdf, 'black')
    pdf.set_font("Arial", "", 12)

    clientes = ClienteMayorista.objects.all()

    if clientes.exists():
        c = 0  # Contador para alternar el color de las filas
        for cliente in clientes:
            c += 1

            # Alternar el color de fondo entre gris y blanco
            if c % 2 == 0:
                bcol_set(pdf, 'gray2')  # Fila gris
            else:
                bcol_set(pdf, 'white')  # Fila blanca
            
            # Dibujar las celdas con el color de fondo establecido
            
            pdf.cell(30, 10, f"{cliente.nombre}", 1, 0, 'C', fill=True)
            pdf.cell(40, 10, f"{cliente.apellido}", 1, 0, 'C', fill=True)
            pdf.cell(40, 10, f"{cliente.cuil}", 1, 0, 'C', fill=True)
            pdf.cell(50, 10, f"{cliente.direccion}", 1, 0, 'C', fill=True)
            pdf.cell(30, 10, f"{cliente.telefono:}", 1, 1, 'C', fill=True)
    else:
        pdf.cell(0, 10, "No hay productos disponibles.", 0, 1, 'C')

    response = HttpResponse(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporteClMyoristas.pdf"'
    return response

