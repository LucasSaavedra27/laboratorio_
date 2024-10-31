from django.db import models
from apps.usuarios.models import Persona, Empleado
from apps.productos.models import Producto
from decimal import Decimal
# Create your models here.

class ClienteMayorista(Persona):
    cuil = models.CharField(max_length=13,blank=False, null=False)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} {self.cuil}"

class Venta(models.Model):
    TIPO_COMPROBANTE = [
        ('A', 'Factura A'),
        ('B', 'Factura B'),
        ('C', 'Factura C'),
    ]
    FORMA_PAGO = [
        ('efectivo','Efectivo'),
        ('transferencia','Transferencia'),
        ('débito','Débito'),
        ('crédito','Crédito'),
    ]
    fechaDeVenta = models.DateField(blank=False, null=False)
    formaDePago = models.CharField(max_length=15, choices=FORMA_PAGO,blank=False, null=False)
    tipoDeComprobante = models.CharField(max_length=15, choices=TIPO_COMPROBANTE,blank=False, null=False)
    clienteMayorista = models.ForeignKey(ClienteMayorista, on_delete=models.SET_NULL, null=True, blank=True,related_name='clienteMayorista')
    total = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    empleado = models.ForeignKey(Empleado,on_delete=models.CASCADE,related_name='ventaEmpleado')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guarda primero la instancia
    
    def calcular_total(self):
        # Calcula el total de todos los detalles de la venta
        self.total = sum(detalle.subTotal for detalle in self.detalleVenta.all())
        self.save(update_fields=['total'])  # Guarda solo el campo total
    
    def __str__(self):
        if self.clienteMayorista is None:
            return f"Venta a consumidor final - {self.fechaDeVenta}"
        else:
            return f"Venta a mayorista {self.clienteMayorista.nombre} - {self.fechaDeVenta}"

class DetalleVenta(models.Model):
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE,related_name='detalleProducto')
    venta = models.ForeignKey(Venta,on_delete=models.CASCADE,related_name='detalleVenta')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2,blank=False, null=False)
    subTotal = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    
    def save(self, *args, **kwargs):
        self.subTotal = self.cantidad * self.producto.precioDeVenta
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.producto.nombre} {self.cantidad} {self.subTotal}"
    
