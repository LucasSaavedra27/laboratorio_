from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name='productos'

urlpatterns = [
    path('',login_required(views.productos),name='productos'),
    path('editarProducto/<producto_id>',login_required(views.editarProducto),name='editarProducto'),
    path('eliminarProducto/<producto_id>',login_required(views.eliminarProducto),name='eliminarProducto'),
    path('edicionProducto/',login_required(views.edicionProducto),name='edicionProducto'),
    path('buscarProducto/', login_required(views.buscarProducto), name='buscarProducto'),
    path('generarPDF/', login_required(views.generarPDF), name='generarPDF'),
    path('agregarProducto/',login_required(views.agregarProducto), name='agregarProducto'),
    path('generarPDF_bajoStock',login_required(views.generarPDF_bajoStock),name='generarPDF_bajoStock'),
    
    path('insumos/',login_required(views.insumos),name='insumos'),
    path('insumos/editar/<insumo_id>',login_required(views.editarInsumo),name='editarInsumo'), #mandar plantilla del insum a editar
    path('insumos/edicion/',login_required(views.edicionInsumo),name='edicionInsumo'),
    path('insumos/eliminar/<insumo_id>',login_required(views.eliminarInsumo),name='eliminarInsumo'),
    path('insumos/buscar/', login_required(views.buscarInsumo), name='buscarInsumo'),
    path('insumos/buscar/editar/<insumo_id>',login_required(views.editarInsumo),name='editarInsumoBuscado'),
    path('insumos/buscar/eliminar/<insumo_id>',login_required(views.eliminarInsumo),name='eliminarInsumoBuscado'),
    path('insumos/generarPDF/', login_required(views.generarPDFInsumoFaltante), name='generarPDFInsumoFaltante'),
]
