from django import forms

from .models import Ingrediente, MovimientoInventario


class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = [
            'nombre',
            'unidad',
            'cantidad_actual',
            'cantidad_minima',
            'costo_unitario',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'unidad': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cantidad_minima': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'costo_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = [
            'ingrediente',
            'tipo',
            'cantidad',
            'motivo',
        ]
        widgets = {
            'ingrediente': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
        }
