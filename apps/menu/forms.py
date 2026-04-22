from django import forms

from apps.inventario.models import Ingrediente

from .models import (
    Categoria,
    ConsumoOpcionMenu,
    Producto,
    RecetaIngrediente,
    RecetaProducto,
)


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


class RecetaProductoForm(forms.ModelForm):
    class Meta:
        model = RecetaProducto
        fields = ['notas', 'activo']
        widgets = {
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RecetaIngredienteForm(forms.ModelForm):
    cantidad = forms.DecimalField(
        label='Gramaje / cantidad por unidad',
        min_value=0.01,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        help_text='Ejemplo: 200 gramos de arroz, 150 gramos de pollo.',
    )

    class Meta:
        model = RecetaIngrediente
        fields = ['ingrediente', 'cantidad']
        widgets = {
            'ingrediente': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        restaurante = kwargs.pop('restaurante', None)
        self.receta = kwargs.pop('receta', None)
        super().__init__(*args, **kwargs)
        qs = Ingrediente.objects.all().order_by('nombre')
        if restaurante is not None:
            qs = qs.filter(restaurante=restaurante)
        self.fields['ingrediente'].queryset = qs

    def clean(self):
        cleaned_data = super().clean()
        ingrediente = cleaned_data.get('ingrediente')
        receta = self.receta or getattr(self.instance, 'receta', None)
        if receta and ingrediente:
            existe = RecetaIngrediente.objects.filter(receta=receta, ingrediente=ingrediente)
            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)
            if existe.exists():
                self.add_error('ingrediente', 'Este ingrediente ya está agregado en la receta.')
        return cleaned_data


class ConsumoOpcionMenuForm(forms.ModelForm):
    cantidad = forms.DecimalField(
        label='Gramaje / cantidad por opción',
        min_value=0.01,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        help_text='Define cuánto se descuenta al elegir esta opción.',
    )

    class Meta:
        model = ConsumoOpcionMenu
        fields = [
            'tipo_menu',
            'categoria_opcion',
            'nombre_opcion',
            'ingrediente',
            'cantidad',
            'activo',
        ]
        widgets = {
            'tipo_menu': forms.Select(attrs={'class': 'form-select'}),
            'categoria_opcion': forms.Select(attrs={'class': 'form-select'}),
            'nombre_opcion': forms.TextInput(attrs={'class': 'form-control'}),
            'ingrediente': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        restaurante = kwargs.pop('restaurante', None)
        self.restaurante = restaurante
        super().__init__(*args, **kwargs)
        qs = Ingrediente.objects.all().order_by('nombre')
        if restaurante is not None:
            qs = qs.filter(restaurante=restaurante)
        self.fields['ingrediente'].queryset = qs
        self.fields['nombre_opcion'].help_text = 'Debe coincidir con el nombre que eliges en el menú del día.'

    def clean(self):
        cleaned_data = super().clean()
        restaurante = self.restaurante or getattr(self.instance, 'restaurante', None)
        ingrediente = cleaned_data.get('ingrediente')
        tipo_menu = cleaned_data.get('tipo_menu')
        categoria_opcion = cleaned_data.get('categoria_opcion')
        nombre_opcion = cleaned_data.get('nombre_opcion')

        if restaurante and ingrediente and tipo_menu and categoria_opcion and nombre_opcion:
            existe = ConsumoOpcionMenu.objects.filter(
                restaurante=restaurante,
                tipo_menu=tipo_menu,
                categoria_opcion=categoria_opcion,
                nombre_opcion=nombre_opcion,
                ingrediente=ingrediente,
            )
            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)
            if existe.exists():
                self.add_error('ingrediente', 'Ese ingrediente ya está configurado para esta opción.')
        return cleaned_data

