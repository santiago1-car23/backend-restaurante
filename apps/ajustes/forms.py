from django import forms
from django.contrib.auth.models import User

from apps.usuarios.models import Empleado, Rol


class UsuarioForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Déjelo en blanco para mantener la contraseña actual.',
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
    )
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        label='Rol',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        labels = {
            'username': 'Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo',
            'is_active': 'Activo',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get('password1')
        pwd2 = cleaned_data.get('password2')
        if pwd1 or pwd2:
            if pwd1 != pwd2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
            if len(pwd1) < 6:
                raise forms.ValidationError('La contraseña debe tener al menos 6 caracteres.')
        return cleaned_data


class EmpleadoExtraForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['telefono', 'direccion', 'hora_entrada', 'hora_salida', 'activo']
        labels = {
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'hora_entrada': 'Hora de entrada',
            'hora_salida': 'Hora de salida',
            'activo': 'Empleado activo',
        }
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'hora_entrada': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_salida': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
