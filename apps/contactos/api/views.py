from rest_framework import viewsets, permissions

from apps.contactos.models import Proveedor, TelefonoNegocio
from .serializers import ProveedorSerializer, TelefonoNegocioSerializer


def _get_restaurante_from_user(user):
    empleado = getattr(user, 'empleado', None)
    return getattr(empleado, 'restaurante', None) if empleado else None


def _user_is_admin(user):
    if user.is_superuser:
        return True
    empleado = getattr(user, 'empleado', None)
    rol = getattr(empleado, 'rol', None) if empleado else None
    nombre_rol = getattr(rol, 'nombre', '') if rol else ''
    return nombre_rol == 'admin'


class IsContactosAdmin(permissions.BasePermission):
    """Solo administradores pueden gestionar contactos (igual que las vistas HTML)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and _user_is_admin(request.user)


class ProveedorViewSet(viewsets.ModelViewSet):
    serializer_class = ProveedorSerializer
    permission_classes = [IsContactosAdmin]

    def get_queryset(self):
        restaurante = _get_restaurante_from_user(self.request.user)
        qs = Proveedor.objects.filter(activo=True)
        if restaurante is not None:
            qs = qs.filter(restaurante=restaurante)
        return qs

    def perform_create(self, serializer):
        restaurante = _get_restaurante_from_user(self.request.user)
        serializer.save(restaurante=restaurante)

    def perform_update(self, serializer):
        restaurante = _get_restaurante_from_user(self.request.user)
        instance = self.get_object()
        if restaurante is not None and instance.restaurante_id is not None and instance.restaurante_id != restaurante.id:
            # Evitar editar proveedores de otro restaurante
            raise permissions.PermissionDenied('No puedes editar proveedores de otro restaurante.')
        serializer.save()

    def perform_destroy(self, instance):
        restaurante = _get_restaurante_from_user(self.request.user)
        if restaurante is not None and instance.restaurante_id is not None and instance.restaurante_id != restaurante.id:
            raise permissions.PermissionDenied('No puedes eliminar proveedores de otro restaurante.')
        instance.delete()


class TelefonoNegocioViewSet(viewsets.ModelViewSet):
    serializer_class = TelefonoNegocioSerializer
    permission_classes = [IsContactosAdmin]

    def get_queryset(self):
        restaurante = _get_restaurante_from_user(self.request.user)
        qs = TelefonoNegocio.objects.filter(activo=True)
        if restaurante is not None:
            qs = qs.filter(restaurante=restaurante)
        return qs

    def perform_create(self, serializer):
        restaurante = _get_restaurante_from_user(self.request.user)
        serializer.save(restaurante=restaurante)

    def perform_update(self, serializer):
        restaurante = _get_restaurante_from_user(self.request.user)
        instance = self.get_object()
        if restaurante is not None and instance.restaurante_id is not None and instance.restaurante_id != restaurante.id:
            raise permissions.PermissionDenied('No puedes editar teléfonos de otro restaurante.')
        serializer.save()

    def perform_destroy(self, instance):
        restaurante = _get_restaurante_from_user(self.request.user)
        if restaurante is not None and instance.restaurante_id is not None and instance.restaurante_id != restaurante.id:
            raise permissions.PermissionDenied('No puedes eliminar teléfonos de otro restaurante.')
        instance.delete()
