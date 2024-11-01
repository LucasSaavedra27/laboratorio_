import os
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from apps.pedidos.models import Proveedor, Pedido, DetallePedido, RecepcionPedido, DetalleRecepcionPedido
from apps.productos.models import Insumo
from apps.usuarios.models import Empleado
from apps.pedidos.forms import FormularioProveedor, FormularioPedido, DetallePedidoFormSet, FormularioRecepcionPedido,DetalleRecepcionPedidoForm
from fpdf import FPDF
from django.conf import settings
from datetime import datetime
from django.http import HttpResponse, JsonResponse

#-------------------------------------PROVEEDORES----------------------------------------------------------
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

#---------------------------------------PEDIDOS--------------------------------------------------------
def pedidos(request):
    pedidos = Pedido.objects.all()  # Obtener todos los pedidos
    mostrar_boton = True  # Variable para controlar la visibilidad del botón
    mostrar_botonPdf = False
    # Obtener todos los insumos y sus precios
    insumos_dict = {insumo.id: insumo.precioInsumo for insumo in Insumo.objects.all()}
    
    if request.method == 'POST':
        pedidoForm = FormularioPedido(request.POST)
        detallePedidoFormset = DetallePedidoFormSet(request.POST)

        if pedidoForm.is_valid() and detallePedidoFormset.is_valid():
            # Guarda el pedido sin calcular el total aún
            pedido = pedidoForm.save(commit=False)

            # Guarda cada detalle y calcula el total después de que el pedido tiene un ID
            totalPedido = 0
            detalles_guardados = False
            for detalle_form in detallePedidoFormset:
                if detalle_form.cleaned_data.get('DELETE'):
                    continue
                if detalle_form.is_valid():
                    detalle = detalle_form.save(commit=False)
                    detalle.pedido = pedido  # Asigna el pedido a cada detalle
                    detalle.save()
                    # Acumula el subtotal de cada detalle en totalPedido
                    totalPedido += detalle.subTotal  # Asegúrate de que `subTotal` esté definido y calculado en `DetallePedido`
                    detalles_guardados = True
                    
            # Actualiza el campo `precioTotalDelPedido` y guarda el pedido
            if detalles_guardados:
                pedido.precioTotalDelPedido = totalPedido
                pedido.save()
                return redirect('/pedidos')
            else:
                pedidoForm.add_error(None, "Se debe agregar al menos un detalle al pedido.")
    else:
        pedidoForm = FormularioPedido()  # Crear un nuevo formulario vacío
        detallePedidoFormset = DetallePedidoFormSet()  # Crear un nuevo formset vacío

    # Renderizar la plantilla con los formularios
    return render(request, 'pedido/pedidos.html', {
        'pedidoForm': pedidoForm,
        'detallePedidoFormset': detallePedidoFormset,
        'pedidos': pedidos,
        'mostrar_boton': mostrar_boton,
        'mostrar_botonPdf':mostrar_botonPdf,
        'insumos_dict': insumos_dict,  # Pasar los precios de los insumos
    })
    
def verDetallePedido(request,pedido_id):
    detallesPedido = DetallePedido.objects.filter(pedido_id=pedido_id)
    pedido = Pedido.objects.get(id=pedido_id)
    if request.path == f'/pedidos/recepcionPedido/verDetallesPedido/{pedido_id}':
        url_retorno = f'/pedidos/recepcionPedido/{pedido_id}'  # Cambia esto a la URL que desees
    else:
        url_retorno = '/pedidos/'
    return render(request, 'pedido/verDetallePedido.html', {
        'detallesPedido': detallesPedido,
        'pedido_id': pedido_id,
        'pedido': pedido,
        'url_retorno': url_retorno
    })

def buscarPedidoPorFecha(request):
    busqueda = request.POST.get('busqueda')  # Obtiene el término de búsqueda de la query
    pedidos = Pedido.objects.all()  # Obtiene todos los pedidos por defecto
    mostrar_botonPdf = True
    if busqueda:  # Si hay un término de búsqueda
        try:
            pedidos = pedidos.filter(fechaPedido=busqueda)
            request.session['pedidos_filtrados'] = busqueda
        except ValueError:
            pedidos = Pedido.objects.none()
    return render(request, 'pedido/pedidos.html', {'pedidos': pedidos, 'busqueda': busqueda, 'mostrar_botonPdf': mostrar_botonPdf})

def actualizarEstadoPedido(request,pedido_id,caracter):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if caracter == 'c':
        pedido.estadoPedido = 'confirmado'
    elif caracter == 'p':
        pedido.estadoPedido = 'pendiente'
    elif caracter == 'x':
        pedido.estadoPedido = 'cancelado'    
    pedido.save()
    return redirect('pedidos:pedidos')

class PDFPedido(FPDF):
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
        self.cell(w = 0, h = 10, txt = 'Pedidos', border = 0, align = 'C', ln=1, fill = 0)
        
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

def generarPDFPedidosPorFecha(request):
    # Crear un objeto FPDF
    pdf = PDFPedido()
    pdf.add_page()
    
    fecha_busqueda = request.session.get('pedidos_filtrados', None)
    if fecha_busqueda:
        try:
            fecha_busqueda_date = datetime.strptime(fecha_busqueda, "%Y-%m-%d").date()
            pedidos = Pedido.objects.filter(fechaPedido=fecha_busqueda_date)
        except ValueError:
            pedidos = Pedido.objects.none()
    else:
        pedidos = Pedido.objects.none()
    # Verificar si hay pedidos
    
    pdf.cell(w=0, h=5, txt=f'FECHA: {fecha_busqueda_date.strftime("%d-%m-%Y")}', border=0, ln=2, align='C', fill=0)
    if pedidos.exists():
        for pedido in pedidos:
            bcol_set(pdf, 'red')  # Color de fondo para títulos
            tcol_set(pdf, 'white')
            pdf.set_font("Arial", "B", 12)
            # Dibujar la cabecera del pedido
            pdf.cell(50, 10, "Pedido n°", 1, 0, 'C', fill=True)
            pdf.cell(60, 10, "Proveedor", 1, 0, 'C', fill=True)
            pdf.cell(40, 10, "Estado", 1, 0, 'C', fill=True)
            pdf.cell(40, 10, "Total", 1, 1, 'C', fill=True)
            
            tcol_set(pdf, 'black')
            pdf.set_font("Arial", "", 12)
            # Dibujar la datos del pedido
            pdf.cell(50, 10, str(pedido.id), 1, 0, 'C', fill=False)
            pdf.cell(60, 10, str(pedido.proveedor), 1, 0, 'C', fill=False)
            pdf.cell(40, 10, pedido.estadoPedido, 1, 0, 'C', fill=False)
            pdf.cell(40, 10, str(pedido.precioTotalDelPedido), 1, 1, 'C', fill=False)

            bcol_set(pdf, 'red')  # Color de fondo para títulos
            tcol_set(pdf, 'white')
            pdf.set_font("Arial", "B", 12)
            # Cabecera de los detalles para cada pedido
            pdf.cell(50, 10, "Insumo", 1, 0, 'C', fill=True)
            pdf.cell(60, 10, "Precio", 1, 0, 'C', fill=True)
            pdf.cell(40, 10, "Cantidad", 1, 0, 'C', fill=True)
            pdf.cell(40, 10, "Subtotal", 1, 1, 'C', fill=True)

            tcol_set(pdf, 'black')
            pdf.set_font("Arial", "", 12)
            # Detalles del pedido
            detalles = DetallePedido.objects.filter(pedido=pedido)
            for detalle in detalles:
                pdf.cell(50, 10, detalle.insumos.nombre, 1, 0, 'C', fill=False)
                pdf.cell(60, 10, str(detalle.insumos.precioInsumo), 1, 0, 'C', fill=False)
                pdf.cell(40, 10, str(detalle.cantidadPedida), 1, 0, 'C', fill=False)
                pdf.cell(40, 10, str(detalle.subTotal), 1, 1, 'C', fill=False)
                
            pdf.cell(0, 10, '', 0, 1)  # Espacio entre diferentes pedidos

    else:
        pdf.cell(0, 10, "No hay pedidos disponibles.", 0, 1, 'C')

    # Preparar la respuesta
    response = HttpResponse(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reportePedidoSegunFecha.pdf"'
    return response

def generarPDFPedidosConfirmados(request):
    # Crear un objeto FPDF
    pdf = PDFPedido()
    pdf.add_page()
    
    pedidos = Pedido.objects.filter(estadoPedido='confirmado')
    pdf.cell(w=0, h=5, txt=f'ESTADO: CONFIRMADO', border=0, ln=2, align='C', fill=0)
    # Verificar si hay pedidos
    if pedidos.exists():
        for pedido in pedidos:
            bcol_set(pdf, 'red')  # Color de fondo para títulos
            tcol_set(pdf, 'white')
            pdf.set_font("Arial", "B", 12)
            # Dibujar la cabecera del pedido
            pdf.cell(50, 10, "Pedido n°", 1, 0, 'C', fill=True)
            pdf.cell(60, 10, "Proveedor", 1, 0, 'C', fill=True)
            pdf.cell(40, 10, "Estado", 1, 0, 'C', fill=True)
            pdf.cell(40, 10, "Total", 1, 1, 'C', fill=True)
            
            tcol_set(pdf, 'black')
            pdf.set_font("Arial", "", 12)
            # Dibujar la datos del pedido
            pdf.cell(50, 10, str(pedido.id), 1, 0, 'C', fill=False)
            pdf.cell(60, 10, str(pedido.proveedor), 1, 0, 'C', fill=False)
            pdf.cell(40, 10, pedido.estadoPedido, 1, 0, 'C', fill=False)
            pdf.cell(40, 10, str(pedido.precioTotalDelPedido), 1, 1, 'C', fill=False)

            bcol_set(pdf, 'red')  # Color de fondo para títulos
            tcol_set(pdf, 'white')
            pdf.set_font("Arial", "B", 12)
            # Cabecera de los detalles para cada pedido
            pdf.cell(50, 10, "Insumo", 1, 0, 'C', fill=True)
            pdf.cell(60, 10, "Precio", 1, 0, 'C', fill=True)
            pdf.cell(40, 10, "Cantidad", 1, 0, 'C', fill=True)
            pdf.cell(40, 10, "Subtotal", 1, 1, 'C', fill=True)

            tcol_set(pdf, 'black')
            pdf.set_font("Arial", "", 12)
            # Detalles del pedido
            detalles = DetallePedido.objects.filter(pedido=pedido)
            for detalle in detalles:
                pdf.cell(50, 10, detalle.insumos.nombre, 1, 0, 'C', fill=False)
                pdf.cell(60, 10, str(detalle.insumos.precioInsumo), 1, 0, 'C', fill=False)
                pdf.cell(40, 10, str(detalle.cantidadPedida), 1, 0, 'C', fill=False)
                pdf.cell(40, 10, str(detalle.subTotal), 1, 1, 'C', fill=False)
                
            pdf.cell(0, 10, '', 0, 1)  # Espacio entre diferentes pedidos

    else:
        pdf.cell(0, 10, "No hay pedidos disponibles.", 0, 1, 'C')

    # Preparar la respuesta
    response = HttpResponse(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reportePedidosConfirmados.pdf"'
    return response

#-------------------------------------RECEPCION PEDIDO----------------------------------------------------------
def recepcionPedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    empleado = get_object_or_404(Empleado, user=request.user)

    # Obtener todos los detalles del pedido
    detalles_pedido = DetallePedido.objects.filter(pedido=pedido)
    recepcionPedido_instance = RecepcionPedido.objects.filter(pedido=pedido).first()
    celdaRecepcion = recepcionPedido_instance is not None  
    mostrar_boton = not celdaRecepcion

    if request.method == "POST":
        recepPedidoForm = FormularioRecepcionPedido(request.POST)

        if recepPedidoForm.is_valid():
            recepcion = recepPedidoForm.save(commit=False)
            recepcion.empleado = empleado
            recepcion.pedido = pedido
            recepcion.save()  # Guarda la recepción primero

            # Procesar cada formulario de DetalleRecepcionPedido
            for i, detalle in enumerate(detalles_pedido):
                cantidad_recibida = request.POST.get(f'cantidadRecibida-{i}')  # Asegúrate de que el nombre sea correcto

                if cantidad_recibida:  # Asegúrate de que no sea None o vacío
                    detalle_recepcion = DetalleRecepcionPedido(
                        recepcionPedido=recepcion,
                        detallePedido=detalle,
                        cantidadRecibida=int(cantidad_recibida),
                    )
                    if detalle.cantidadPedida > int(cantidad_recibida):
                        detalle_recepcion.estado = 'incompleto'
                    elif detalle.cantidadPedida == int(cantidad_recibida):
                        detalle_recepcion.estado = 'completo'
                    else:
                        detalle_recepcion.estado = 'erroneo'

                    detalle_recepcion.save()

                    # Actualizar la cantidad disponible del insumo
                    insumo = detalle.insumos
                    insumo.cantidadDisponible += int(cantidad_recibida)
                    insumo.save()

            return redirect('pedidos:recepcionDePedido', pedido_id=pedido.id)

    else:
        recepPedidoForm = FormularioRecepcionPedido(initial={'fechaDeRecepcion': '', 'pedido': pedido}, empleado=empleado)

    return render(request, 'recepcionPedido/recepcionDelPedido.html', {
        'pedido': pedido,
        'detallesPedido': detalles_pedido,
        'recepPedidoForm': recepPedidoForm,
        'celdaRecepcion': celdaRecepcion,
        'mostrar_boton':mostrar_boton
    })

    
def verDetallesRecepcionPedido(request, pedido_id): 
    recepcionPedido = get_object_or_404(RecepcionPedido, pedido__id=pedido_id)
    detallesRecepcionPedido = DetalleRecepcionPedido.objects.filter(recepcionPedido_id=recepcionPedido.id)  # Usa `recepcionPedido.id`
    
    return render(request, 'recepcionPedido/detalleRecepcionPedido.html', {
        'detallesRecepcionPedido': detallesRecepcionPedido,
        'recepcionPedido': recepcionPedido
    })

def obtener_precio_Insumo(request, insumo_id):
    try:
        insumo = Insumo.objects.get(id=insumo_id)
        return JsonResponse({'precio': str(insumo.precioInsumo)})
    except Insumo.DoesNotExist:
        return JsonResponse({'error': 'Insumo no encontrado'}, status=404)

class PDFRecepcionPedido(FPDF):
    def header(self):
        logo = os.path.join(settings.BASE_DIR, 'static', 'img', 'logotipo.png')
        
        # Verificar si el archivo existe
        if os.path.exists(logo):
            self.image(logo, x=10, y=5, w=35, h=35) 
        
        self.set_font('Arial', '', 15)

        tcol_set(self, 'red')
        tfont_size(self,30)
        tfont(self,'B')
        self.cell(w = 0, h = 10, txt = 'Reporte de', border = 0, ln=1,
                align = 'C', fill = 0)
        self.cell(w = 0, h = 15, txt = 'Recepción', border = 0, align = 'C', ln=1, fill = 0)
        
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
             
def generarPDFRecepPedido(request,pedido_id):
    # Crear un objeto FPDF
    pdf = PDFRecepcionPedido()
    pdf.add_page()
    
    pedido = Pedido.objects.get(id=pedido_id)
    recepcion = RecepcionPedido.objects.get(pedido=pedido)
    # pdf.cell(w=0, h=5, txt=f'PEDIDO: {pedido_id}', border=0, ln=2, align='C', fill=0)
    # Verificar si hay pedidos
    if pedido:
        
        #---------------------------recepcion-------------------------
        pdf.cell(w=0, h=5, txt=f'RECEPCION: {recepcion.id}', border=0, ln=2, align='C', fill=0)
        bcol_set(pdf, 'red')  # Color de fondo para títulos
        tcol_set(pdf, 'white')
        pdf.set_font("Arial", "B", 12)
        # Dibujar la cabecera de Recepcion
        pdf.cell(100, 10, "Empleado", 1, 0, 'C', fill=True)
        pdf.cell(45, 10, "Fecha Recepción", 1, 0, 'C', fill=True)
        pdf.cell(45, 10, "Pedido Recibido", 1, 1, 'C', fill=True)
        
        tcol_set(pdf, 'black')
        pdf.set_font("Arial", "", 12)
        # Dibujar la datos del pedido
        pdf.cell(100, 10, str(recepcion.empleado), 1, 0, 'C', fill=False)
        pdf.cell(45, 10, str(recepcion.fechaDeRecepcion), 1, 0, 'C', fill=False)
        pdf.cell(45, 10, str(recepcion.pedido.id), 1, 1, 'C', fill=False)

        bcol_set(pdf, 'red')  # Color de fondo para títulos
        tcol_set(pdf, 'white')
        pdf.set_font("Arial", "B", 12)
        
        pdf.cell(0, 10, '', 0, 1)  # Espacio entre recepcion y detalles
        
        # Cabecera de los detalles para cada pedido
        pdf.cell(50, 10, "Insumo", 1, 0, 'C', fill=True)
        pdf.cell(35, 10, "Unidad Medida", 1, 0, 'C', fill=True)
        pdf.cell(35, 10, "Cantidad Pedida", 1, 0, 'C', fill=True)
        pdf.cell(40, 10, "Cantidad Recibida", 1, 0, 'C', fill=True)
        pdf.cell(30, 10, "Estado", 1, 1, 'C', fill=True)

        tcol_set(pdf, 'black')
        pdf.set_font("Arial", "", 12)
        # Detalles de la recepcion
        detalles = DetalleRecepcionPedido.objects.filter(recepcionPedido=recepcion)
        for detalle in detalles:
            pdf.cell(50, 10, detalle.detallePedido.insumos.nombre, 1, 0, 'C', fill=False)
            pdf.cell(35, 10, detalle.detallePedido.insumos.unidadDeMedida, 1, 0, 'C', fill=False)
            pdf.cell(35, 10, str(detalle.detallePedido.cantidadPedida), 1, 0, 'C', fill=False)
            pdf.cell(40, 10, str(detalle.cantidadRecibida), 1, 0, 'C', fill=False)
            pdf.cell(30, 10, detalle.estado, 1, 1, 'C', fill=False)
    
    else:   
        pdf.cell(0, 10, "No hay pedidos disponibles.", 0, 1, 'C')

    # Preparar la respuesta
    response = HttpResponse(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporteRecepcionPedido.pdf"'
    return response
#---------------------------------------PDF PROVEEDORES--------------------------------------------------------
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

