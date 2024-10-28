from django.forms.models import inlineformset_factory
from django import forms
from .models import ClienteMayorista, Venta,DetalleVenta

class FormularioVenta(forms.ModelForm):
    class Meta:
        model = Venta
        fields = [
            'fechaDeVenta', 
            'formaDePago', 
            'tipoDeComprobante', 
            'clienteMayorista', 
            
        ]
        labels = {
            'fechaDeVenta': 'Fecha de venta',
            'formaDePago': 'Forma de pago',
            'tipoDeComprobante': 'Tipo de comprobante',
            'clienteMayorista': 'Cliente mayorista',
        }  
        widgets = {
            'fechaDeVenta': forms.TextInput(attrs={'type': 'date','class': 'form-control'}),
            'formaDePago': forms.Select(attrs={'class': 'form-control'}),
            'tipoDeComprobante': forms.Select(attrs={'class': 'form-control'}),
            'clienteMayorista': forms.Select(attrs={'type': 'date','class': 'form-control'}),
        }
        
class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad']
        labels = {
            'producto': 'Producto',
            'cantidad': 'Cantidad',
        }
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control','step': '0.01'}),
        }
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        producto = self.cleaned_data.get('producto')
        
        if cantidad > producto.cantidadDisponible:
            raise forms.ValidationError(f"Solo hay {producto.cantidadDisponible} unidades disponibles de {producto.nombre}.")
        
        return cantidad

DetalleVentaFormSet = inlineformset_factory(
    Venta, 
    DetalleVenta,  # Venta y DetalleVenta son los modelos relacionados
    form=DetalleVentaForm,
    extra=1,  # comienza mostrando 1 formulario
    can_delete=True  # permite borrar el formulario
)

class FormularioMayorista(forms.ModelForm):
    class Meta:
        model = ClienteMayorista
        fields = ['nombre', 'apellido','cuil', 'direccion','telefono', 'mail']
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'cuil': 'CUIL',
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            'mail': 'Email',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'cuil': forms.TextInput(attrs={'class': 'form-control','maxlength': '13'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'mail': forms.TextInput(attrs={'class': 'form-control'}),
        }


