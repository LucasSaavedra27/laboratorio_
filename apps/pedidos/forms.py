from django import forms
from .models import Proveedor, Pedido, DetallePedido, Insumo

from django.forms.models import inlineformset_factory

#-------------------------------------PROVEEDORES----------------------------------------------------------
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
        
#---------------------------------------PEDIDOS--------------------------------------------------------
class FormularioPedido(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'proveedor', 
            'fechaPedido',
            'estadoPedido',  
        ]
        labels = {
            'proveedor': 'Dni Proveedor',
            'fechaPedido': 'Fecha Pedido',
            'estadoPedido': 'Estado',
        }
        CATEGORIA_CHOICES = [
            ('recibido', 'Recibido'),
            ('pendiente', 'Pendiente'),
        ]   
        widgets = {
            
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'fechaPedido': forms.TextInput(attrs={'class': 'form-control'}),
            'estadoPedido': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        error_messages = {
            'proveedor': {
                'required': 'Ingresar Proveedores.',
            },
            'fechaPedido': {
                'required': 'Ingresa fecha de pedido.',
            },
           'estadoPedido': {
                'required': 'ingresa el estado del pedido.',
            },
        }
        
class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['insumos', 'cantidadPedida','observaciones']
        labels = {
            'insumos': 'Insumos',
            'cantidadPedida': 'Cantidad',
            'observaciones': 'Observaciones',
        }
        widgets = {
            'insumos': forms.Select(attrs={'class': 'form-control'}),
            'cantidadPedida': forms.NumberInput(attrs={'class': 'form-control','step': '0.01'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidadPedida')
        insumo = self.cleaned_data.get('insumos')
        
        if insumo is not None and cantidad > insumo.cantidadDisponible:
            raise forms.ValidationError(f"Solo hay {insumo.cantidadDisponible} unidades disponibles de {insumo.nombre}.")
        
        return cantidad
    
DetallePedidoFormSet = inlineformset_factory(
    Pedido, 
    DetallePedido,  # Pedido y DetallePedido son los modelos relacionados
    form=DetallePedidoForm,
    extra=1,  # comienza mostrando 1 formulario
    can_delete=True  # permite borrar el formulario
)
        