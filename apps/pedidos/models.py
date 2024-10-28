from django.db import models
from apps.productos.models import Insumo
from apps.usuarios.models import Persona,Empleado

# Create your models here.

class Proveedor(Persona):
    ESTADO = [
        ('activo', 'Activo'), 
        ('inactivo', 'Inactivo'),
    ]
    dni  = models.CharField(max_length=8,blank=False,null=False)
    estado = models.CharField(max_length=10, choices=ESTADO,blank=False, null=False)
    empresa = models.CharField(max_length=50,blank=False,null=False)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} {self.dni}" 

class Pedido(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE,related_name = 'proveedor')
    ESTADO_PEDIDO = [
        ('confirmado', 'Confirmado'),
        ('pendiente', 'Pendiente'),
        ('cancelado', 'Cancelado'),
    ]
    fechaPedido = models.DateField(blank=False,null=False)
    estadoPedido = models.CharField(max_length=10,choices=ESTADO_PEDIDO,blank=False,null=False)
    precioTotalDelPedido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    
    def __str__(self):
        return f"{self.fechaPedido} {self.estadoPedido}"
    
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido,null=True, on_delete=models.CASCADE, related_name='detalles')
    insumos = models.ForeignKey(Insumo,on_delete=models.CASCADE,related_name='insumos')
    cantidadPedida = models.PositiveIntegerField(blank=False,null=False)
    observaciones = models.TextField()
    subTotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Calcular el subtotal basado en la cantidad y el precio del insumo
        self.subTotal = self.cantidadPedida * self.insumos.precioInsumo  # Asegúrate de que Insumo tenga un campo `precio`
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Detalle {self.id} - Insumo: {self.insumos} - Cantidad: {self.cantidadPedida}" 
    
class RecepcionPedido(models.Model):
    empleado = models.ForeignKey(Empleado,on_delete=models.CASCADE,related_name='empleado')
    fechaDeRecepcion = models.DateField(blank=False,null=False)
    
    def __str__(self):
        return f"{self.empleado.nombre} {self.empleado.apellido} {self.fechaDeRecepcion}"
    
class DetalleRecepcionPedido(models.Model):
    detallePedido = models.ForeignKey(DetallePedido,on_delete=models.CASCADE,related_name='detalleRecepcionPedido')
    
    ESTADO = [
        ('completo','Completo'),
        ('incompleto','Incompleto'),
    ]
    cantidadRecibida = models.PositiveBigIntegerField(blank=False, null=False)
    estado = models.CharField(max_length=10,choices=ESTADO,blank=False,null=False)
    
    def __str__(self):
        return f"{self.detallePedido.insumos.nombre} {self.cantidadRecibida}"
    

    