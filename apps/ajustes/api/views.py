from django.contrib.auth.models import User
from rest_framework import viewsets, permissions

from apps.usuarios.models import Empleado, Rol
from .serializers import EmpleadoSerializer, RolSerializer


def _es_admin(user: User) -> bool:
    try:
        return bool(user.empleado and user.empleado.rol and user.empleado.rol.nombre == 'admin')
    except Empleado.DoesNotExist:
        return False


class IsAjustesAdmin(permissions.BasePermission):
    """Solo los usuarios con rol admin pueden gestionar ajustes de usuarios."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and _es_admin(request.user)


class EmpleadoViewSet(viewsets.ModelViewSet):
    """Gestión de empleados/usuarios por restaurante (igual que vistas de ajustes)."""

    serializer_class = EmpleadoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Empleado.objects.all().select_related('user', 'rol')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class RolViewSet(viewsets.ReadOnlyModelViewSet):
    """Listado de roles disponibles para asignar a empleados."""

    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Rol.objects.all()
