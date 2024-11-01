from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name='pedidos'

urlpatterns = [
    path('proveedores/',login_required(views.proveedores),name='proveedores'),
    path('proveedores/editar/<proveedor_id>',login_required(views.editarProveedor),name='editarProveedor'), #mandar plantilla del prov a editar
    path('proveedores/eliminar/<proveedor_id>',login_required(views.eliminarProveedor),name='eliminarProveedor'),
    path('proveedores/edicion/',login_required(views.edicionProveedor),name='edicionProveedor'),
    path('proveedores/buscar/', login_required(views.buscarProveedor), name='buscarProveedor'),
    path('proveedores/buscar/editar/<proveedor_id>',login_required(views.editarProveedor),name='editarProveedorBuscado'),
    path('proveedores/buscar/eliminar/<proveedor_id>',login_required(views.eliminarProveedor),name='eliminarProveedorBuscado'),
    path('proveedores/generarPDF/', login_required(views.generarPDF), name='generarPDF'),
    
    path('pedidos/',login_required(views.pedidos),name='pedidos'),
    path('pedidos/verDetallesPedido/<pedido_id>',login_required(views.verDetallePedido),name='verDetallePedido'),
    path('pedidos/buscar/', login_required(views.buscarPedidoPorFecha), name='buscarPorFecha'),
    path('pedidos/buscar/generarPDF/', login_required(views.generarPDFPedidos), name='generarPDFPedidos'),
    path('pedidos/generarPDF/', login_required(views.generarPDFPedidosConfirmados), name='generarPDFPedConfir'),
    path('pedidos/<pedido_id>/<str:caracter>/',login_required(views.actualizarEstadoPedido),name='actualizarPedido'),
    path('obtener-precio-insumo/<insumo_id>/', login_required(views.obtener_precio_Insumo), name='obtener_precio_insumo'), #fetch para el subtotal
    
    path('pedidos/recepcionPedido/<pedido_id>',login_required(views.recepcionPedido),name='recepcionDePedido'),
    path('pedidos/recepcionPedido/<pedido_id>/generarPDF/',login_required(views.generarPDFRecepPedido),name='generarPDFrecepcion'),
    path('pedidos/recepcionPedido/verDetallesPedido/<pedido_id>',login_required(views.verDetallePedido),name='verDetallePedidoDesdeRecepcion'),
    path('pedidos/recepcionPedido/verDetallesRecepcion/<pedido_id>',login_required(views.verDetallesRecepcionPedido),name='verDetallesRecepcionPedido'),

]