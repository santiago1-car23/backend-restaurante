from django.contrib.auth.models import User
from rest_framework import serializers

from apps.usuarios.models import Empleado, Rol


class EmpleadoSerializer(serializers.Serializer):
    """Serializer para crear/editar empleados + usuario asociado.

    Replica la lógica de UsuarioForm + EmpleadoExtraForm.
    """

    id = serializers.IntegerField(read_only=True)

    # Campos de User
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(default=True)

    # Gestión de contraseña (opcional en update)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    # Rol y datos extra de Empleado
    rol = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all())
    telefono = serializers.CharField(max_length=15, required=False, allow_blank=True)
    direccion = serializers.CharField(required=False, allow_blank=True)
    hora_entrada = serializers.TimeField(required=False, allow_null=True)
    hora_salida = serializers.TimeField(required=False, allow_null=True)
    activo = serializers.BooleanField(default=True)

    def validate_password(self, value):
        if value and len(value) < 6:
            raise serializers.ValidationError('La contraseña debe tener al menos 6 caracteres.')
        return value

    def create(self, validated_data):
        request = self.context['request']
        empleado_admin = getattr(request.user, 'empleado', None)
        restaurante = getattr(empleado_admin, 'restaurante', None) if empleado_admin else None

        password = validated_data.pop('password', '') or ''
        rol = validated_data.pop('rol')
        telefono = validated_data.pop('telefono', '')
        direccion = validated_data.pop('direccion', '')
        hora_entrada = validated_data.pop('hora_entrada', None)
        hora_salida = validated_data.pop('hora_salida', None)
        activo = validated_data.pop('activo', True)

        # Crear usuario
        user = User(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            is_active=validated_data.get('is_active', True),
        )
        if password:
            user.set_password(password)
        user.save()

        empleado = Empleado.objects.create(
            user=user,
            rol=rol,
            restaurante=restaurante,
            telefono=telefono,
            direccion=direccion,
            hora_entrada=hora_entrada,
            hora_salida=hora_salida,
            activo=activo,
        )
        return empleado

    def update(self, instance: Empleado, validated_data):
        user = instance.user

        password = validated_data.pop('password', '') or ''
        rol = validated_data.pop('rol', instance.rol)
        telefono = validated_data.pop('telefono', instance.telefono)
        direccion = validated_data.pop('direccion', instance.direccion)
        hora_entrada = validated_data.pop('hora_entrada', instance.hora_entrada)
        hora_salida = validated_data.pop('hora_salida', instance.hora_salida)
        activo = validated_data.pop('activo', instance.activo)

        user.username = validated_data.get('username', user.username)
        user.first_name = validated_data.get('first_name', user.first_name)
        user.last_name = validated_data.get('last_name', user.last_name)
        user.email = validated_data.get('email', user.email)
        user.is_active = validated_data.get('is_active', user.is_active)
        if password:
            user.set_password(password)
        user.save()

        instance.rol = rol
        instance.telefono = telefono
        instance.direccion = direccion
        instance.hora_entrada = hora_entrada
        instance.hora_salida = hora_salida
        instance.activo = activo
        instance.save()
        return instance

    def to_representation(self, instance: Empleado):
        user = instance.user
        return {
            'id': instance.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_active': user.is_active,
            'rol': instance.rol.id if instance.rol else None,
            'rol_nombre': instance.rol.nombre if instance.rol else None,
            'telefono': instance.telefono,
            'direccion': instance.direccion,
            'hora_entrada': instance.hora_entrada,
            'hora_salida': instance.hora_salida,
            'activo': instance.activo,
        }


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']
