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
    path('proveedores/buscar/eliminar/<proveedor_id>',views.eliminarProveedor,name='editarProveedorBuscado'),
    path('proveedores/generarPDF/', views.generarPDF, name='generarPDF'),
]