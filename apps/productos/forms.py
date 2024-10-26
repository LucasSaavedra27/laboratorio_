from decimal import Decimal,InvalidOperation
from django import forms
from .models import Producto

class FormularioProducto(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 
            'precioDeVenta', 
            'precioDeCosto', 
            'fechaDeElaboracion', 
            'fechaDeVencimiento', 
            'categoria', 
            'cantidadDisponible', 
            'cantidadMinRequerida',
        ]
        labels = {
            'nombre': 'Nombre del Producto',
            'precioDeVenta': 'Precio de Venta',
            'precioDeCosto': 'Precio de Costo',
            'fechaDeElaboracion': 'Fecha de Elaboración',
            'fechaDeVencimiento': 'Fecha de Vencimiento',
            'categoria': 'Categoría',
            'cantidadDisponible': 'Cantidad Disponible',
            'cantidadMinRequerida': 'Cantidad Mínima Requerida',
        }
        CATEGORIA_CHOICES = [
            ('panaderia', 'Panadería'),
            ('pasteleria', 'Pastelería'),
        ]   
        widgets = {
            
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precioDeVenta': forms.TextInput(attrs={'class': 'form-control'}),
            'precioDeCosto': forms.TextInput(attrs={'class': 'form-control'}),
            'fechaDeElaboracion': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),
            'fechaDeVencimiento': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}), 
            'cantidadDisponible': forms.NumberInput(attrs={'class': 'form-control'}),
            'cantidadMinRequerida': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
        error_messages = {
            'nombre': {
                'required': 'Por favor ingresa el nombre del producto.',
            },
            'precioDeVenta': {
                'required': 'Por favor ingresa el precio de venta.',
            },
           'precioDeVenta': {
                'required': 'Por favor ingresa el precio de costo.',
            },
           'fechaDeElaboracion': {
                'required': 'Por favor ingresa la fecha de elaboracion.',
            },
           'fechaDeVencimiento': {
                'required': 'Por favor ingresa la fecha de vencimiento.',
            },
           'categoria': {
                'required': 'Por favor ingresa la categoria.',
            },
           'cantidadDisponible': {
                'required': 'Por favor ingresa la cantidad disponible.',
            },
           'cantidadMinRequerida': {
                'required': 'Por favor ingresa la cantidad mínima requerida.',
            },
        }
        

