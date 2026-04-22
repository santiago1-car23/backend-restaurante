from datetime import date

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.currency import formatear_pesos_colombianos
from apps.menu.models import (
    Categoria,
    ConsumoOpcionMenu,
    MenuDiario,
    Producto,
    RecetaIngrediente,
    RecetaProducto,
)
from .serializers import (
    CategoriaSerializer,
    ConsumoOpcionMenuSerializer,
    ProductoSerializer,
    RecetaIngredienteSerializer,
    RecetaProductoSerializer,
)

PRODUCTOS_TECNICOS_MENU = ['Menu corriente', 'Menu desayuno']


class IsStaffOrReadOnlyMenu(permissions.BasePermission):
    """Lectura para autenticados, escritura solo para staff/superuser."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and (request.user.is_staff or request.user.is_superuser)


def _restaurante_de_usuario(user):
    empleado = getattr(user, 'empleado', None)
    return getattr(empleado, 'restaurante', None) if empleado else None


class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    permission_classes = [IsStaffOrReadOnlyMenu]

    def get_queryset(self):
        restaurante = _restaurante_de_usuario(self.request.user)
        qs = Categoria.objects.filter(activo=True)
        if restaurante:
            qs = qs.filter(restaurante=restaurante)
        return qs.order_by('nombre')


class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    permission_classes = [IsStaffOrReadOnlyMenu]

    def get_queryset(self):
        restaurante = _restaurante_de_usuario(self.request.user)
        categoria_id = self.request.query_params.get('categoria')
        query = (self.request.query_params.get('q') or '').strip()

        qs = Producto.objects.filter(disponible=True).exclude(
            nombre__in=PRODUCTOS_TECNICOS_MENU
        ).select_related('categoria')
        if restaurante:
            qs = qs.filter(categoria__restaurante=restaurante)
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)
        if query:
            from django.db.models import Q

            qs = qs.filter(
                Q(nombre__icontains=query) | Q(descripcion__icontains=query)
            )
        return qs.order_by('categoria__nombre', 'nombre')


class RecetaProductoViewSet(viewsets.ModelViewSet):
    serializer_class = RecetaProductoSerializer
    permission_classes = [IsStaffOrReadOnlyMenu]

    def get_queryset(self):
        restaurante = _restaurante_de_usuario(self.request.user)
        qs = RecetaProducto.objects.select_related('producto', 'producto__categoria').prefetch_related('ingredientes__ingrediente')
        if restaurante:
            qs = qs.filter(producto__categoria__restaurante=restaurante)
        return qs.order_by('producto__nombre')


class RecetaIngredienteViewSet(viewsets.ModelViewSet):
    serializer_class = RecetaIngredienteSerializer
    permission_classes = [IsStaffOrReadOnlyMenu]

    def get_queryset(self):
        restaurante = _restaurante_de_usuario(self.request.user)
        qs = RecetaIngrediente.objects.select_related('receta', 'receta__producto', 'ingrediente')
        receta_id = self.request.query_params.get('receta')
        if restaurante:
            qs = qs.filter(receta__producto__categoria__restaurante=restaurante)
        if receta_id:
            qs = qs.filter(receta_id=receta_id)
        return qs.order_by('receta__producto__nombre', 'ingrediente__nombre')


class ConsumoOpcionMenuViewSet(viewsets.ModelViewSet):
    serializer_class = ConsumoOpcionMenuSerializer
    permission_classes = [IsStaffOrReadOnlyMenu]

    def get_queryset(self):
        restaurante = _restaurante_de_usuario(self.request.user)
        qs = ConsumoOpcionMenu.objects.select_related('ingrediente', 'restaurante')
        if restaurante:
            qs = qs.filter(restaurante=restaurante)
        tipo_menu = self.request.query_params.get('tipo_menu')
        categoria_opcion = self.request.query_params.get('categoria_opcion')
        if tipo_menu:
            qs = qs.filter(tipo_menu=tipo_menu)
        if categoria_opcion:
            qs = qs.filter(categoria_opcion=categoria_opcion)
        return qs.order_by('tipo_menu', 'categoria_opcion', 'nombre_opcion', 'ingrediente__nombre')

    def perform_create(self, serializer):
        serializer.save(restaurante=_restaurante_de_usuario(self.request.user))


class MenuDiaView(APIView):
    """Devuelve el menú corriente y de desayuno del día para el restaurante del usuario.

    Estructura similar a las vistas menu_corriente y menu_desayuno.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        fecha_str = request.query_params.get('fecha')
        if fecha_str:
            try:
                fecha_sel = date.fromisoformat(fecha_str)
            except ValueError:
                fecha_sel = date.today()
        else:
            fecha_sel = date.today()

        restaurante = _restaurante_de_usuario(request.user)
        if not restaurante:
            return Response(
                {
                    'fecha': fecha_sel.isoformat(),
                    'menu_corriente': None,
                    'menu_desayuno': None,
                }
            )

        menu_obj, _ = MenuDiario.objects.get_or_create(fecha=fecha_sel, restaurante=restaurante)

        def _split_lista(valor: str):
            return [v.strip() for v in valor.split(',') if v.strip()] if valor else []

        menu_corriente = {
            'sopa': menu_obj.sopa,
            'principio': _split_lista(menu_obj.principios),
            'proteina': _split_lista(menu_obj.proteinas),
            'acompanante': menu_obj.acompanante,
            'limonada': menu_obj.limonada,
            'precio_sopa': menu_obj.precio_sopa,
            'precio_sopa_formateado': formatear_pesos_colombianos(menu_obj.precio_sopa),
            'precio_bandeja': menu_obj.precio_bandeja,
            'precio_bandeja_formateado': formatear_pesos_colombianos(menu_obj.precio_bandeja),
            'precio_completo': menu_obj.precio_completo,
            'precio_completo_formateado': formatear_pesos_colombianos(menu_obj.precio_completo),
        }

        menu_desayuno = {
            'principales': _split_lista(menu_obj.desayuno_principales),
            'bebidas': _split_lista(menu_obj.desayuno_bebidas),
            'caldos': _split_lista(menu_obj.caldos),
            'acompanante': menu_obj.desayuno_acompanante,
            'precio_desayuno': menu_obj.precio_desayuno,
            'precio_desayuno_formateado': formatear_pesos_colombianos(menu_obj.precio_desayuno),
        }

        return Response(
            {
                'fecha': fecha_sel.isoformat(),
                'menu_corriente': menu_corriente,
                'menu_desayuno': menu_desayuno,
            }
        )
