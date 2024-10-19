from django import forms
from .models import Proveedor

class FormularioProveedor(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'nombre', 
            'apellido',
            'dni', 
            'direccion', 
            'telefono', 
            'mail',  
            'estado', 
            'empresa',
        ]
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'dni': 'Dni',
            'direccion': 'Dirección',
            'telefono': 'Teléfono o Celular',
            'mail': 'Email',
            'estado': 'Estado',
            'empresa': 'Empresa',
        }
        CATEGORIA_CHOICES = [
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo'),
        ]   
        widgets = {
            
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Donde habita actualmente'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'mail': forms.EmailInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}), 
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de empresa a la que pertenece'}),
        }
        
        error_messages = {
            'nombre': {
                'required': 'Por favor ingresa el nombre del proveedor.',
            },
            'apellido': {
                'required': 'Por favor ingresa el apellido del proveedor.',
            },
           'dni': {
                'required': 'Por favor ingresa el DNI del proveedor.',
            },
           'direccion': {
                'required': 'Por favor ingresa la direccion del proveedor.',
            },
           'telefono': {
                'required': 'Por favor ingresa el telefono del proveedor.',
            },
           'mail': {
                'required': 'Por favor ingresa el mail del proveedor.',
            },
           'estado': {
                'required': 'Por favor ingresa el estado en que se encuentra el proveedor.',
            },
           'empresa': {
                'required': 'Por favor ingresa la empresa a la que pertenece el proveedor.',
            },
        }