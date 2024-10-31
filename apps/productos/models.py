from django.db import models

# Create your models here.

class Producto(models.Model):
    CATEGORIAS = [
        ('panadería','Panadería'),
        ('pastelería','Pastelería'),
    ]
    UNIDADES_MEDIDA = [
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('u', 'Unidades'),
        ('paq', 'Paquete'),
        ('caja', 'Caja'),
        ('taza', 'Taza'),
        ('otro', 'Otro'),
    ]
    nombre = models.CharField(max_length=50,blank=False,null=False)
    precioDeVenta = models.DecimalField(max_digits=10, decimal_places=2,blank=False,null=False)
    precioDeCosto = models.DecimalField(max_digits=10, decimal_places=2,blank=False,null=False)
    fechaDeElaboracion = models.DateField(blank=False,null=False)
    fechaDeVencimiento = models.DateField(blank=False,null=False)
    categoria = models.CharField(max_length=15,choices=CATEGORIAS,blank=False,null=False)
    unidadDeMedida = models.CharField(max_length=10,choices=UNIDADES_MEDIDA,blank=False,null=False,default='unidad')
    cantidadDisponible = models.DecimalField(max_digits=10, decimal_places=2,blank=False,null=False)
    cantidadMinRequerida = models.PositiveIntegerField(blank=False,null=False)
    
    def __str__(self):
        return self.nombre

class Insumo(models.Model):
    UNIDADES_MEDIDA = [
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('u', 'Unidades'),
        ('paq', 'Paquete'),
        ('caja', 'Caja'),
        ('taza', 'Taza'),
        ('otro', 'Otro'),
    ]
    nombre = models.CharField(max_length=50,blank=False,null=False)
    unidadDeMedida = models.CharField(max_length=10,choices=UNIDADES_MEDIDA,blank=False,null=False)
    cantidadDisponible = models.PositiveIntegerField(blank=False,null=False)
    cantidadMinRequerida = models.PositiveIntegerField(blank=False,null=False)
    precioInsumo = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=True, default=0.0)
    
    def __str__(self):
        return self.nombre