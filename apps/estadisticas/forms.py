from django import forms
from datetime import datetime
import locale


locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  

class SeleccionarFechaForm(forms.Form):
    # Generar opciones de mes en español
    MES_CHOICES = [(i, datetime(1, i, 1).strftime('%B')) for i in range(1, 13)]
    ANIO_CHOICES = [(i, i) for i in range(2020, datetime.now().year + 1)]

    mes = forms.ChoiceField(choices=MES_CHOICES, label="Mes")
    anio = forms.ChoiceField(choices=ANIO_CHOICES, label="Año")

    def __init__(self, *args, **kwargs):
        default_month = kwargs.pop('default_month', datetime.now().month)  # Mes actual
        default_year = kwargs.pop('default_year', datetime.now().year)  # Año actual
        super().__init__(*args, **kwargs)
        self.fields['mes'].initial = default_month
        self.fields['anio'].initial = default_year
        self.fields['mes'].widget.attrs.update({'class': 'form-control'})
        self.fields['anio'].widget.attrs.update({'class': 'form-control'})