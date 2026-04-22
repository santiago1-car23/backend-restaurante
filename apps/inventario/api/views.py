from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.inventario.models import Ingrediente, MovimientoInventario
from apps.menu.models import Producto
from .serializers import (
    IngredienteSerializer,
    MovimientoInventarioSerializer,
    RegistrarMovimientoSerializer,
)


def _puede_gestionar_inventario(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    empleado = getattr(user, 'empleado', None)
    rol = getattr(empleado, 'rol', None) if empleado else None
    nombre_rol = getattr(rol, 'nombre', None)
    return nombre_rol == 'admin'


def _restaurante_de_usuario(user):
    empleado = getattr(user, 'empleado', None)
    return getattr(empleado, 'restaurante', None) if empleado else None


class IsInventarioStaff(permissions.BasePermission):
    """Permisos para gestionar inventario (crear/editar/eliminar)."""

    def has_permission(self, request, view):
        # Lectura: cualquier usuario autenticado puede ver su inventario
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Escritura: solo quien pueda gestionar inventario (como en vistas HTML)
        return _puede_gestionar_inventario(request.user)


class IngredienteViewSet(viewsets.ModelViewSet):
    """API para ingredientes de inventario.

    - Lista ingredientes del restaurante del usuario.
    - Permite crear/editar/eliminar ingredientes si el usuario tiene permisos.
    - Incluye campo `alerta_stock` como en la vista.
    """

    serializer_class = IngredienteSerializer
    permission_classes = [IsInventarioStaff]

    def get_queryset(self):
        request = self.request
        empleado = getattr(request.user, 'empleado', None)
        restaurante = getattr(empleado, 'restaurante', None) if empleado else None

        if restaurante:
            ingredientes = Ingrediente.objects.filter(restaurante=restaurante)
        else:
            if request.user.is_superuser:
                ingredientes = Ingrediente.objects.all()
            else:
                ingredientes = Ingrediente.objects.none()

        query = (request.query_params.get('q') or '').strip()
        solo_bajo_stock = request.query_params.get('criticos') == '1'

        if query:
            ingredientes = ingredientes.filter(nombre__icontains=query)

        if solo_bajo_stock:
            ingredientes = [i for i in ingredientes if i.alerta_stock()]

        return ingredientes

    def perform_create(self, serializer):
        restaurante = _restaurante_de_usuario(self.request.user)
        serializer.save(restaurante=restaurante)

    def perform_destroy(self, instance):
        nombre_ing = instance.nombre
        restaurante_ing = instance.restaurante
        instance.delete()

        try:
            if restaurante_ing is not None:
                Producto.objects.filter(
                    nombre=nombre_ing,
                    categoria__restaurante=restaurante_ing,
                ).delete()
            else:
                Producto.objects.filter(
                    nombre=nombre_ing,
                    categoria__restaurante__isnull=True,
                ).delete()
        except Exception:
            pass

    @action(detail=False, methods=['post'], url_path='sincronizar-productos')
    def sincronizar_productos(self, request):
        """Sincroniza productos del menú como ingredientes si no existen.

        Replica la lógica de inventario_list que crea ingredientes a partir de productos.
        """
        restaurante = _restaurante_de_usuario(request.user)
        if not restaurante:
            return Response({'detail': 'El usuario no tiene restaurante asignado.'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.menu.models import Producto as ProductoMenu

        productos_menu = ProductoMenu.objects.filter(categoria__restaurante=restaurante)
        creados = 0
        for producto in productos_menu:
            qs_ing = Ingrediente.objects.filter(nombre=producto.nombre, restaurante=restaurante)
            if not qs_ing.exists():
                Ingrediente.objects.create(
                    restaurante=restaurante,
                    nombre=producto.nombre,
                    unidad='unidad',
                    cantidad_actual=0,
                    cantidad_minima=0,
                    costo_unitario=producto.precio,
                )
                creados += 1

        return Response({'creados': creados})


class MovimientoInventarioViewSet(viewsets.ReadOnlyModelViewSet):
    """API para listar y registrar movimientos de inventario."""

    serializer_class = MovimientoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated, IsInventarioStaff]

    def get_queryset(self):
        request = self.request
        empleado = getattr(request.user, 'empleado', None)
        restaurante = getattr(empleado, 'restaurante', None) if empleado else None

        movimientos = MovimientoInventario.objects.select_related('ingrediente', 'usuario')

        if restaurante and not request.user.is_superuser:
            movimientos = movimientos.filter(ingrediente__restaurante=restaurante)
        elif not restaurante and not request.user.is_superuser:
            movimientos = movimientos.none()

        ingrediente_id = request.query_params.get('ingrediente')
        tipo = request.query_params.get('tipo')

        if ingrediente_id:
            movimientos = movimientos.filter(ingrediente_id=ingrediente_id)
        if tipo:
            movimientos = movimientos.filter(tipo=tipo)

        return movimientos

    @action(detail=False, methods=['post'], url_path='registrar')
    def registrar(self, request):
        """Registra un nuevo movimiento de inventario (entrada/salida/ajuste)."""
        if not _puede_gestionar_inventario(request.user):
            return Response({'detail': 'No tienes permiso para gestionar el inventario.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = RegistrarMovimientoSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        movimiento = MovimientoInventario.objects.create(
            ingrediente=serializer.validated_data['ingrediente'],
            tipo=serializer.validated_data['tipo'],
            cantidad=serializer.validated_data['cantidad'],
            motivo=serializer.validated_data['motivo'],
            usuario=request.user,
        )

        return Response(MovimientoInventarioSerializer(movimiento).data, status=status.HTTP_201_CREATED)
