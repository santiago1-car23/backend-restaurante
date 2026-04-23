from django.contrib.auth.models import User
from rest_framework import serializers

from apps.usuarios.models import Empleado, Rol, Notificacion


class EmpleadoInlineSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    restaurante_id = serializers.IntegerField(source='restaurante.id', read_only=True)
    restaurante_nombre = serializers.CharField(source='restaurante.nombre', read_only=True)

    class Meta:
        model = Empleado
        fields = [
            'id', 'rol', 'rol_nombre', 'restaurante_id', 'restaurante_nombre',
            'telefono', 'direccion', 'hora_entrada', 'hora_salida', 'activo',
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    empleado = EmpleadoInlineSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'empleado',
        ]


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = [
            'id', 'mensaje', 'url', 'creada', 'leida',
        ]
        read_only_fields = ['creada']
