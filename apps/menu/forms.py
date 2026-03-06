from django import forms

from .models import Producto, Categoria


class ProductoForm(forms.ModelForm):
    stock_inicial = forms.DecimalField(
        label='Stock en inventario (unidades)',
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
    )

    class Meta:
        model = Producto
        fields = [
            'nombre',
            'descripcion',
            'precio',
            'categoria',
            'imagen',
            'disponible',
            'tiempo_preparacion',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tiempo_preparacion': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        # Permitir pasar el restaurante explícitamente desde la vista
        restaurante = kwargs.pop('restaurante', None)
        super().__init__(*args, **kwargs)

        # Si el producto ya existe, precargar el stock desde inventario si hay ingrediente
        if self.instance and self.instance.pk:
            try:
                from apps.inventario.models import Ingrediente

                qs = Ingrediente.objects.filter(nombre=self.instance.nombre)
                if restaurante is not None:
                    qs = qs.filter(restaurante=restaurante)

                ingrediente = qs.first()
                if ingrediente is not None:
                    self.fields['stock_inicial'].initial = ingrediente.cantidad_actual
            except Exception:
                # Si no hay ingrediente asociado, simplemente dejamos el campo vacío
                pass


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = [
            'nombre',
            'descripcion',
            'activo',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        # No exponemos el restaurante en el formulario; se asigna en la vista
        super().__init__(*args, **kwargs)

