from django.urls import path
from . import views

app_name='ventas'

urlpatterns = [
    path('',views.ventas,name='ventas'),
    path('agregarVenta/',views.agregarVenta,name='agregarVenta'),
    path('verDetallesVenta/<venta_id>',views.verDetallesVenta,name='verDetallesVenta'),
    path('buscarVentas/',views.buscarVentas,name='buscarVentas'),
    path('exportarPDF/',views.exportarPDF,name='exportarPDF'),
] 