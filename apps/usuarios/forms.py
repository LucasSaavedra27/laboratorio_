
from django import forms
from .models import Empleado
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellido', 'dni', 'direccion', 'telefono', 'mail', 'fechaDeNacimiento', 'fechaDeIngreso', 'salario','user','estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control'}), 
            'apellido': forms.TextInput(attrs={'class':'form-control'}), 
            'dni': forms.TextInput(attrs={'class':'form-control'}), 
            'direccion': forms.TextInput(attrs={'class':'form-control'}), 
            'telefono': forms.TextInput(attrs={'class':'form-control'}),  
            'mail': forms.EmailInput(attrs={'class': 'form-control'}),
            'salario': forms.NumberInput(attrs={'class':'form-control'}),
            'estado': forms.Select(attrs={'class':'form-control'}),
            'fechaDeNacimiento': forms.DateInput(attrs={'type': 'date','class':'form-control'}),
            'fechaDeIngreso': forms.DateInput(attrs={'type': 'date','class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_active=True)  # Mostrar solo usuarios activos
        
class CrearUsuario(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clase 'form-control' a todos los campos del formulario
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Las contraseñas no coinciden."), code='password_mismatch')
        
        if len(password2) < 8:
            raise forms.ValidationError(_("La contraseña debe tener al menos 8 caracteres."), code='password_too_short')
        
        return password2

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_("Este nombre de usuario ya está en uso."), code='username_taken')
        return username