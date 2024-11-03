from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Persona(models.Model):
    nombre = models.CharField(max_length=50,blank=False,null=False)
    apellido = models.CharField(max_length=50,blank=False,null=False)
    direccion  = models.CharField(max_length=50,blank=False,null=False)
    telefono = models.CharField(max_length=15,blank=False,null=False)
    mail = models.EmailField(blank=True,null=True)
    
    class Meta:
        abstract = True  # Esto hace que no se genere una tabla en la BD
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Empleado(Persona):
    ESTADO = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='user')
    dni  = models.CharField(max_length=8,blank=False,null=False)
    fechaDeNacimiento = models.DateField(blank=False,null=False)
    fechaDeIngreso = models.DateField(blank=False,null=False)
    salario = models.DecimalField(max_digits=10,blank=False,null=False,decimal_places=2)
    estado = models.CharField(max_length=10,choices=ESTADO,blank=False,null=False,default='activo')
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}, DNI: {self.dni}"
    