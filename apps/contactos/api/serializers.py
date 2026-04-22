from rest_framework import serializers

from apps.contactos.models import Proveedor, TelefonoNegocio


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = [
            'id', 'restaurante', 'nombre', 'telefono', 'telefono_secundario',
            'email', 'direccion', 'tipo', 'notas', 'activo',
            'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['restaurante', 'creado_en', 'actualizado_en']


class TelefonoNegocioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelefonoNegocio
        fields = [
            'id', 'restaurante', 'nombre', 'numero', 'notas', 'activo',
            'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['restaurante', 'creado_en', 'actualizado_en']
