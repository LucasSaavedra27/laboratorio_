from django.contrib import admin
from .models import Venta, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1  # Número de formularios vacíos adicionales para agregar detalles

class VentaAdmin(admin.ModelAdmin):
    list_display = ('fechaDeVenta', 'formaDePago', 'tipoDeComprobante', 'clienteMayorista', 'total', 'empleado')
    list_filter = ('formaDePago', 'tipoDeComprobante', 'empleado', 'fechaDeVenta')
    search_fields = ('clienteMayorista__nombre', 'empleado__nombre', 'fechaDeVenta')  # Busca por nombre del cliente o empleado
    inlines = [DetalleVentaInline]  # Añade los detalles de la venta en la misma página

admin.site.register(Venta, VentaAdmin)
