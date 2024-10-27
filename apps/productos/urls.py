from django.urls import path
from . import views

app_name='productos'

urlpatterns = [
    path('',views.productos,name='productos'),
    path('editarProducto/<producto_id>',views.editarProducto,name='editarProducto'),
    path('eliminarProducto/<producto_id>',views.eliminarProducto,name='eliminarProducto'),
    path('edicionProducto/',views.edicionProducto,name='edicionProducto'),
    path('buscarProducto/', views.buscarProducto, name='buscarProducto'),
    path('generarPDF/', views.generarPDF, name='generarPDF'),
    path('agregarProducto/',views.agregarProducto, name='agregarProducto'),
    
    path('insumos/',views.insumos,name='insumos'),
    path('insumos/editar/<insumo_id>',views.editarInsumo,name='editarInsumo'), #mandar plantilla del insum a editar
    path('insumos/edicion/',views.edicionInsumo,name='edicionInsumo'),
    path('insumos/eliminar/<insumo_id>',views.eliminarInsumo,name='eliminarInsumo'),
    path('insumos/buscar/', views.buscarInsumo, name='buscarInsumo'),
    path('insumos/buscar/editar/<insumo_id>',views.editarInsumo,name='editarInsumoBuscado'),
    path('insumos/buscar/eliminar/<insumo_id>',views.eliminarInsumo,name='eliminarInsumoBuscado'),
    path('insumos/generarPDF/', views.generarPDFInsumoFaltante, name='generarPDFInsumoFaltante'),
]
