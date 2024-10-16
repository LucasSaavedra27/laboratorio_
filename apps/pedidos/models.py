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
    precioTotalDelPedido = models.DecimalField(max_digits=10, decimal_places=2,blank=False,null=False)
    
    def __str__(self):
        return f"{self.fechaPedido} {self.estadoPedido}"
    
class DetallePedido(models.Model):
    insumos = models.ForeignKey(Insumo,on_delete=models.CASCADE,related_name='insumos')
    cantidadPedida = models.PositiveIntegerField(blank=False,null=False)
    observaciones = models.TextField()
    
    def __str__(self):
        return 
    
class RecepcionPedido(models.Model):
    empleado = models.ForeignKey(Empleado,on_delete=models.CASCADE,related_name='empleado')
    fechaDeRecepcion = models.DateField(blank=False,null=False)
    
    def __str__(self):
        return f"{self.empleado.nombre} {self.empleado.apellido} {self.fechaDeRecepcion}"
    
class DetalleRecepcionPedido(models.Model):
    detallePedido = models.ForeignKey(DetallePedido,on_delete=models.CASCADE,related_name='detallePedido')
    
    ESTADO = [
        ('completo','Completo'),
        ('incompleto','Incompleto'),
    ]
    cantidadRecibida = models.PositiveBigIntegerField(blank=False, null=False)
    estado = models.CharField(max_length=10,choices=ESTADO,blank=False,null=False)
    
    def __str__(self):
        return f"{self.detallePedido.insumos.nombre} {self.cantidadRecibida}"
    

    