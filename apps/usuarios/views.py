
from django.conf import settings
from datetime import datetime
import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from fpdf import FPDF
from Panaderia import settings
from .forms import EmpleadoForm, CrearUsuario
from django.contrib.auth.models import User
from apps.usuarios.models import Empleado
from django.contrib import messages

def empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'usuarios/empleados.html', {'empleados': empleados})

def buscarEmpleado(request):
    busqueda = request.POST['busqueda']
    empleados = Empleado.objects.all()
    if busqueda: 
        empleados = empleados.filter(dni__icontains=busqueda)
    return render(request, 'usuarios/empleados.html', {'empleados': empleados, 'busqueda': busqueda})

def eliminarEmpleado(request,empleado_id):
    empleado = Empleado.objects.get(id=empleado_id)
    empleado.estado='inactivo'
    empleado.save()
    return redirect('usuarios:empleados')

def editarEmpleado(request,empleado_id):
    empleado = Empleado.objects.get(id=empleado_id)
    return render(request,'usuarios/edicionEmpleados.html',{'empleado':empleado})

def edicionEmpleado(request):
    if request.method == 'POST':  
        empleado_id = request.POST.get('id')
        empleado = Empleado.objects.get(id=empleado_id)
        empleado.nombre = request.POST['nombre']
        empleado.apellido = request.POST['apellido']
        empleado.dni = request.POST['dni']
        empleado.direccion = request.POST['direccion']
        empleado.telefono = request.POST['telefono']
        empleado.mail = request.POST['mail']
        empleado.fechaDeNacimiento = request.POST['fechaDeNacimiento']
        empleado.salario = request.POST['salario']
        empleado.fechaDeIngreso = request.POST['fechaDeIngreso']
        empleado.estado = request.POST['estado']
        empleado.save()  
        
    return redirect('usuarios:empleados')  


def agregarEmpleado(request):
    if request.method == "POST":
        form = EmpleadoForm(request.POST)
        if form.is_valid(): 
            form.save()
            messages.success(request, "Empleado agregado con éxito.")
            return redirect('usuarios:empleados')  
    else:
        form = EmpleadoForm() 
    return render(request, 'usuarios/agregarEmpleado.html', {'form': form})

def crear_usuario(request):
    if request.method == "POST":
        form = CrearUsuario(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Usuario creado con éxito.")
            return redirect('usuarios:agregarEmpleado')  
    else:
        form = CrearUsuario()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})

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
    def __init__(self, title):
        super().__init__()
        self.title = title
    
    def header(self):
        logo = os.path.join(settings.BASE_DIR, 'static', 'img', 'logotipo.png')
        
        # Verificar si el archivo existe
        if os.path.exists(logo):
            self.image(logo, x=10, y=10, w=30, h=30) 
        
        self.set_font('Arial', '', 15)

        tcol_set(self, 'red')
        tfont_size(self,30)
        tfont(self,'B')
        self.cell(w = 0, h = 20, txt = self.title, border = 0, ln=1,
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
    pdf = PDF("Reporte de empleados")
    pdf.add_page()
    
    # Configuración de la tabla
    # Cambiar el color del fondo a verde para los títulos de la tabla
    bcol_set(pdf, 'red')  # Establece el color verde para el fondo de las celdas
    tcol_set(pdf, 'white')
    pdf.set_font("Arial", "B", 12)

    # Dibujar las celdas de los títulos con fondo verde
    pdf.cell(33, 10, "Nombre", 1, 0, 'C', fill=True)
    pdf.cell(33, 10, "Apellido", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "DNI", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "Telefono", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "Salario", 1, 0, 'C', fill=True)
    pdf.cell(33, 10, "Fecha ingreso", 1, 1, 'C', fill=True)

    tcol_set(pdf, 'black')
    # Cambiar el estilo de fuente para el contenido
    pdf.set_font("Arial", "", 12)

    # Obtener todos los productos de la base de datos
    empleados = Empleado.objects.all()

    # Verificar si hay productos
    if empleados.exists():
        c = 0  # Contador para alternar el color de las filas
        for empleado in empleados:
            c += 1

            # Alternar el color de fondo entre gris y blanco
            if c % 2 == 0:
                bcol_set(pdf, 'gray2')  # Fila gris
            else:
                bcol_set(pdf, 'white')  # Fila blanca
            
            if empleado.estado=='activo':
                pdf.cell(33, 10, f"{empleado.nombre}", 1, 0, 'C', fill=True)
                pdf.cell(33, 10, f"{empleado.apellido}", 1, 0, 'C', fill=True)
                pdf.cell(30, 10, f"{empleado.dni}", 1, 0, 'C', fill=True)
                pdf.cell(30, 10, f"{empleado.telefono}", 1, 0, 'C', fill=True)
                pdf.cell(30, 10, f"${empleado.salario}", 1, 0, 'C', fill=True) 
                pdf.cell(33, 10, f"{empleado.fechaDeIngreso}", 1, 1, 'C', fill=True)
            else:
                c-=1
    else:
        pdf.cell(0, 10, "No hay productos disponibles.", 0, 1, 'C')

    # Preparar la respuesta
    response = HttpResponse(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporteProductos.pdf"'
    return response