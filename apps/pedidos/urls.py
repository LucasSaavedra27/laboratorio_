from django.urls import path
from . import views

app_name='pedidos'

urlpatterns = [
    path('proveedores/',views.proveedores,name='proveedores'),
    path('proveedores/editar/<proveedor_id>',views.editarProveedor,name='editarProveedor'), #mandar plantilla del prov a editar
    path('proveedores/eliminar/<proveedor_id>',views.eliminarProveedor,name='eliminarProveedor'),
    path('proveedores/edicion/',views.edicionProveedor,name='edicionProveedor'),
    path('proveedores/buscar/', views.buscarProveedor, name='buscarProveedor'),
    path('proveedores/buscar/editar/<proveedor_id>',views.editarProveedor,name='editarProveedorBuscado'),
    path('proveedores/buscar/eliminar/<proveedor_id>',views.eliminarProveedor,name='eliminarProveedorBuscado'),
    path('proveedores/generarPDF/', views.generarPDF, name='generarPDF'),
    
    path('pedidos/',views.pedidos,name='pedidos'),
    path('pedidos/verDetallesPedido/<pedido_id>',views.verDetallePedido,name='verDetallePedido'),
    path('pedidos/buscar/', views.buscarPedidoPorFecha, name='buscarPorFecha'),
    path('pedidos/buscar/generarPDF/', views.generarPDFPedidosPorFecha, name='generarPDFPedidos'),
    path('pedidos/generarPDF/', views.generarPDFPedidosConfirmados, name='generarPDFPedConfir'),
    path('pedidos/<pedido_id>/<str:caracter>/',views.actualizarEstadoPedido,name='actualizarPedido'),
    
    path('pedidos/recepcionPedido/<pedido_id>',views.recepcionPedido,name='recepcionDePedido'),
    path('pedidos/recepcionPedido/verDetallesPedido/<pedido_id>',views.verDetallePedido,name='verDetallePedidoDesdeRecepcion'),
    path('pedidos/recepcionPedido/verDetallesRecepcion/<pedido_id>',views.verDetallesRecepcionPedido,name='verDetallesRecepcionPedido'),
]