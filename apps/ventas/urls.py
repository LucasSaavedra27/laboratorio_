from django.urls import path
from . import views,views_mayoristas
from django.contrib.auth.decorators import login_required

app_name='ventas'

urlpatterns = [
    path('',login_required(views.ventas),name='ventas'),
    path('agregarVenta/',login_required(views.agregarVenta) ,name='agregarVenta'),
    path('verDetallesVenta/<venta_id>',login_required(views.verDetallesVenta),name='verDetallesVenta'),
    path('buscarVentas/',login_required(views.buscarVentas),name='buscarVentas'),
    path('exportarPDF/',login_required(views.exportarPDF),name='exportarPDF'),
    path('listadoMayoristas/',login_required(views_mayoristas.listadoMayoristas),name='listadoMayoristas'),
    path('agregarMayorista/',login_required(views_mayoristas.agregarMayorista),name='agregarMayorista'),
    path('editarMayorista/<mayorista_id>',login_required(views_mayoristas.editarMayorista),name='editarMayorista'),
    path('edicionMayorista/',login_required(views_mayoristas.edicionMayorista),name='edicionMayorista'),
    path('buscarMayorista/',login_required(views_mayoristas.buscarMayorista),name='buscarMayorista'),
    path('exportarPDF_Mayoristas/',login_required(views_mayoristas.exportarPDF_Mayoristas),name='exportarPDF_Mayoristas'),
    path('obtener-precio-producto/<producto_id>/', login_required(views.obtener_precio_producto), name='obtener_precio_producto'),
] 