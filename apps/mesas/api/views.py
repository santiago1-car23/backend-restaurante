from rest_framework import viewsets, permissions

from apps.mesas.models import Mesa
from .serializers import MesaSerializer


class IsStaffOrReadOnly(permissions.BasePermission):
    """Permite lectura a usuarios autenticados y escritura solo a staff.

    Esto refleja la lógica actual de las vistas HTML, donde solo staff puede
    crear/editar/eliminar mesas.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class MesaViewSet(viewsets.ModelViewSet):
    """API REST para gestionar mesas.

    - Lista solo mesas activas del restaurante asociado al empleado.
    - Permite crear/editar/eliminar solo a usuarios staff.
    """

    serializer_class = MesaSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        qs = Mesa.objects.filter(activa=True)
        empleado = getattr(self.request.user, 'empleado', None)
        restaurante = getattr(empleado, 'restaurante', None) if empleado else None
        if restaurante is not None:
            qs = qs.filter(restaurante=restaurante)
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        disponibles = self.request.query_params.get('disponibles')
        if disponibles in ['1', 'true', 'True']:
            qs = qs.filter(estado='libre')
        return qs.order_by('numero')

    def perform_create(self, serializer):
        """Forzar que la mesa pertenezca al restaurante del empleado, si existe."""
        empleado = getattr(self.request.user, 'empleado', None)
        restaurante = getattr(empleado, 'restaurante', None) if empleado else None
        serializer.save(restaurante=restaurante)

    def perform_update(self, serializer):
        """Evitar que se cambie de restaurante vía API, mantener la lógica actual."""
        empleado = getattr(self.request.user, 'empleado', None)
        restaurante = getattr(empleado, 'restaurante', None) if empleado else None
        serializer.save(restaurante=restaurante)
