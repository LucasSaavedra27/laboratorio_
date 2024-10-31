from django.contrib import admin

from apps.usuarios.models import Empleado

# Register your models here.
@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre','apellido','direccion','telefono','mail','user','dni','fechaDeNacimiento','fechaDeIngreso','salario')
    search_fields = ('nombre','apellido','user','dni')
    