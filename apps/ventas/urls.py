from django.urls import path
from . import views,views_mayoristas

app_name='ventas'

urlpatterns = [
    path('',views.ventas,name='ventas'),
    path('agregarVenta/',views.agregarVenta,name='agregarVenta'),
    path('verDetallesVenta/<venta_id>',views.verDetallesVenta,name='verDetallesVenta'),
    path('buscarVentas/',views.buscarVentas,name='buscarVentas'),
    path('exportarPDF/',views.exportarPDF,name='exportarPDF'),
    path('listadoMayoristas/',views_mayoristas.listadoMayoristas,name='listadoMayoristas'),
    path('agregarMayorista/',views_mayoristas.agregarMayorista,name='agregarMayorista'),
    path('editarMayorista/<mayorista_id>',views_mayoristas.editarMayorista,name='editarMayorista'),
    path('edicionMayorista/',views_mayoristas.edicionMayorista,name='edicionMayorista'),
    path('buscarMayorista/',views_mayoristas.buscarMayorista,name='buscarMayorista'),
    path('exportarPDF_Mayoristas/',views_mayoristas.exportarPDF_Mayoristas,name='exportarPDF_Mayoristas'),
] 