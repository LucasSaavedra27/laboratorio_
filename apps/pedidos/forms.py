from django import forms
from .models import Proveedor, Pedido, DetallePedido, RecepcionPedido, DetalleRecepcionPedido

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
            'proveedor': 'Proveedor',
            'fechaPedido': 'Fecha Pedido',
            'estadoPedido': 'Estado',
        } 
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'fechaPedido': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),
            'estadoPedido': forms.Select(attrs={'class': 'form-control'}),
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
        error_messages = {
            'insumos': {
                'required': 'Ingresar fecha de recepción.',
            },
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
#---------------------------------------RECEPCIONPEDIDOS--------------------------------------------------------
class FormularioRecepcionPedido(forms.ModelForm):
    class Meta:
        model = RecepcionPedido
        fields = [
            'empleado', 
            'fechaDeRecepcion',
            'pedido'
        ]
        labels = {
            'empleado': 'Empleado',
            'fechaDeRecepcion': 'Fecha de Recepción',
            'pedido': 'pedido',
        } 
        widgets = {
            'empleado': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'fechaDeRecepcion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pedido': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
        
        error_messages = {
            'fechaDeRecepcion': {
                'required': 'Ingresar fecha de recepción.',
            },
        }
        
class DetalleRecepcionPedidoForm(forms.ModelForm):
    class Meta:
        model = DetalleRecepcionPedido
        fields = ['detallePedido', 'cantidadRecibida']
        labels = {
            'detallePedido': 'Detalle',
            'cantidadRecibida': 'Cantidad Recibida',
        } 
        widgets = {
            'detallePedido': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'cantidadRecibida': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

DetalleRecepcionPedidoFormSet = forms.inlineformset_factory(
    RecepcionPedido,
    DetalleRecepcionPedido,
    form=DetalleRecepcionPedidoForm,
    extra=0,  # Número de formularios adicionales
    can_delete=True  # Permite eliminar instancias
)