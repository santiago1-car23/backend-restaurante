from datetime import date

from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.currency import formatear_pesos_colombianos
from apps.menu.inventario import (
    construir_consumos_opciones_menu,
    validar_stock_consumos,
)
from apps.menu.api.serializers import CategoriaSerializer, ProductoSerializer
from apps.menu.models import Categoria, Producto
from apps.pedidos.models import DetallePedido, Pedido
from .serializers import (
    ActualizarDetallePedidoSerializer,
    ActualizarPedidoSerializer,
    CrearDetallePedidoSerializer,
    CrearPedidoSerializer,
    DetallePedidoSerializer,
    PedidoSerializer,
)
from ..services import (
    ESTADOS_PEDIDO_ACTIVOS,
    caja_abierta,
    liberar_mesa_si_no_hay_pedidos_activos,
    menu_del_dia_data,
    notificar_mesero_pedido_listo,
    puede_marcar_servido,
    puede_escribir_pedidos,
    restaurante_usuario,
)

PRODUCTOS_TECNICOS_MENU = ['Menu corriente', 'Menu desayuno']


def _pedido_actualizado(pedido_id):
    return (
        Pedido.objects
        .select_related('mesa', 'mesero')
        .prefetch_related('detalles__producto')
        .get(pk=pedido_id)
    )


class PedidosPermission(permissions.BasePermission):
    """Permisos alineados con la operación real del restaurante."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        if getattr(view, 'action', '') == 'marcar_servido':
            return puede_marcar_servido(request.user)

        return puede_escribir_pedidos(request.user)


class PedidoViewSet(viewsets.ModelViewSet):
    """API principal de pedidos para Expo."""

    serializer_class = PedidoSerializer
    permission_classes = [PedidosPermission]

    def get_queryset(self):
        restaurante = restaurante_usuario(self.request.user)
        if not caja_abierta(restaurante):
            return Pedido.objects.none()

        qs = Pedido.objects.select_related('mesa', 'mesero').prefetch_related('detalles__producto')
        if restaurante:
            qs = qs.filter(restaurante=restaurante)

        archivado = self.request.query_params.get('archivado')
        if archivado in ['0', 'false', 'False']:
            qs = qs.filter(archivado=False)
        elif archivado in ['1', 'true', 'True']:
            qs = qs.filter(archivado=True)

        incluir_cancelados = self.request.query_params.get('incluir_cancelados')
        if incluir_cancelados not in ['1', 'true', 'True']:
            qs = qs.exclude(estado='cancelado')

        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

        mesa_id = self.request.query_params.get('mesa')
        if mesa_id:
            qs = qs.filter(mesa_id=mesa_id)

        query = (self.request.query_params.get('q') or '').strip()
        if query:
            qs = qs.filter(
                Q(observaciones__icontains=query)
                | Q(mesa__numero__icontains=query)
                | Q(mesero__username__icontains=query)
                | Q(mesero__first_name__icontains=query)
                | Q(mesero__last_name__icontains=query)
                | Q(detalles__producto__nombre__icontains=query)
            ).distinct()

        return qs.order_by('-fecha_creacion')

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ActualizarPedidoSerializer
        return super().get_serializer_class()

    def perform_update(self, serializer):
        pedido = serializer.save()
        pedido.calcular_total()

        if pedido.estado not in ESTADOS_PEDIDO_ACTIVOS:
            liberar_mesa_si_no_hay_pedidos_activos(pedido.mesa, excluir_pedido_id=pedido.id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if hasattr(instance, 'factura'):
            return Response(
                {'detail': 'No puedes editar un pedido pagado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(PedidoSerializer(instance, context={'request': request}).data)

    def destroy(self, request, *args, **kwargs):
        pedido = self.get_object()
        if hasattr(pedido, 'factura'):
            return Response(
                {'detail': 'No puedes eliminar un pedido pagado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        mesa = pedido.mesa
        response = super().destroy(request, *args, **kwargs)
        liberar_mesa_si_no_hay_pedidos_activos(mesa)
        return response

    @action(detail=False, methods=['post'], url_path='abrir')
    def abrir_pedido(self, request):
        restaurante = restaurante_usuario(request.user)
        if not caja_abierta(restaurante):
            return Response({'detail': 'La caja está cerrada. Debes abrirla para gestionar pedidos.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CrearPedidoSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        pedido = serializer.save()
        return Response(PedidoSerializer(pedido, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='catalogo')
    def catalogo(self, request, pk=None):
        """Devuelve el contexto equivalente a la vista HTML de detalle."""

        pedido = self.get_object()
        restaurante = getattr(pedido, 'restaurante', None)
        if not caja_abierta(restaurante):
            return Response({'detail': 'La caja está cerrada.'}, status=status.HTTP_400_BAD_REQUEST)

        categoria_id = request.query_params.get('categoria')
        query = (request.query_params.get('q') or '').strip()
        show_corriente = request.query_params.get('corriente') == '1'
        show_desayuno = request.query_params.get('desayuno') == '1'

        categorias_qs = Categoria.objects.filter(activo=True)
        if restaurante:
            categorias_qs = categorias_qs.filter(restaurante=restaurante)
        categorias_qs = categorias_qs.order_by('nombre')

        categoria_corriente = categorias_qs.filter(nombre__iexact='corriente').first()
        categoria_desayuno = categorias_qs.filter(nombre__iexact='desayuno').first()
        categoria_snacks = categorias_qs.filter(nombre__iexact='snacks').first()

        productos_qs = Producto.objects.filter(disponible=True).exclude(
            nombre__in=PRODUCTOS_TECNICOS_MENU
        ).select_related('categoria')
        if restaurante:
            productos_qs = productos_qs.filter(categoria__restaurante=restaurante)
        if categoria_id:
            productos_qs = productos_qs.filter(categoria_id=categoria_id)
        if query:
            productos_qs = productos_qs.filter(
                Q(nombre__icontains=query) | Q(descripcion__icontains=query)
            )
        productos_qs = productos_qs.order_by('categoria__nombre', 'nombre')

        menu_obj, menu_corriente, menu_desayuno = menu_del_dia_data(restaurante)
        fecha_sel = date.today()
        if menu_obj:
            if menu_corriente:
                menu_corriente['precio_sopa_formateado'] = formatear_pesos_colombianos(menu_obj.precio_sopa)
                menu_corriente['precio_bandeja_formateado'] = formatear_pesos_colombianos(menu_obj.precio_bandeja)
                menu_corriente['precio_completo_formateado'] = formatear_pesos_colombianos(menu_obj.precio_completo)
            if menu_desayuno:
                menu_desayuno['precio_desayuno_formateado'] = formatear_pesos_colombianos(menu_obj.precio_desayuno)

        return Response(
            {
                'pedido': PedidoSerializer(pedido, context={'request': request}).data,
                'categorias': CategoriaSerializer(categorias_qs, many=True).data,
                'productos': ProductoSerializer(productos_qs, many=True).data,
                'categoria_id': int(categoria_id) if categoria_id and categoria_id.isdigit() else None,
                'query': query,
                'show_corriente': show_corriente,
                'show_desayuno': show_desayuno,
                'categoria_corriente_id': categoria_corriente.id if categoria_corriente else None,
                'categoria_desayuno_id': categoria_desayuno.id if categoria_desayuno else None,
                'categoria_snacks_id': categoria_snacks.id if categoria_snacks else None,
                'menu_corriente': menu_corriente,
                'menu_desayuno': menu_desayuno,
                'fecha_menu': fecha_sel.isoformat() if fecha_sel else None,
            }
        )

    @action(detail=True, methods=['post'], url_path='agregar-detalle')
    def agregar_detalle(self, request, pk=None):
        pedido = self.get_object()
        if not caja_abierta(getattr(pedido, 'restaurante', None)):
            return Response({'detail': 'La caja está cerrada. No puedes modificar pedidos.'}, status=status.HTTP_400_BAD_REQUEST)
        if hasattr(pedido, 'factura'):
            return Response({'detail': 'No puedes agregar productos a un pedido pagado.'}, status=status.HTTP_400_BAD_REQUEST)
        detalle_serializer = CrearDetallePedidoSerializer(
            data=request.data,
            context={'request': request, 'pedido': pedido},
        )
        detalle_serializer.is_valid(raise_exception=True)
        detalle = detalle_serializer.save()
        pedido = _pedido_actualizado(pedido.id)
        return Response(
            {
                'detalle': DetallePedidoSerializer(detalle).data,
                'pedido': PedidoSerializer(pedido, context={'request': request}).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'], url_path='menu-dia')
    def menu_dia(self, request, pk=None):
        pedido = self.get_object()
        restaurante = getattr(pedido, 'restaurante', None)
        if not caja_abierta(restaurante):
            return Response({'detail': 'La caja está cerrada.'}, status=status.HTTP_400_BAD_REQUEST)
        menu_obj, menu_corriente, menu_desayuno = menu_del_dia_data(restaurante)
        fecha_sel = date.today()
        if menu_obj:
            if menu_corriente:
                menu_corriente['precio_sopa_formateado'] = formatear_pesos_colombianos(menu_obj.precio_sopa)
                menu_corriente['precio_bandeja_formateado'] = formatear_pesos_colombianos(menu_obj.precio_bandeja)
                menu_corriente['precio_completo_formateado'] = formatear_pesos_colombianos(menu_obj.precio_completo)
            if menu_desayuno:
                menu_desayuno['precio_desayuno_formateado'] = formatear_pesos_colombianos(menu_obj.precio_desayuno)
        return Response(
            {
                'pedido_id': pedido.id,
                'fecha': fecha_sel.isoformat() if fecha_sel else None,
                'menu_corriente': menu_corriente,
                'menu_desayuno': menu_desayuno,
            }
        )

    @action(detail=True, methods=['post'], url_path='agregar-corriente')
    def agregar_corriente(self, request, pk=None):
        pedido = self.get_object()
        restaurante = getattr(pedido, 'restaurante', None)
        if not caja_abierta(restaurante):
            return Response({'detail': 'La caja está cerrada. No puedes modificar pedidos.'}, status=status.HTTP_400_BAD_REQUEST)
        if hasattr(pedido, 'factura'):
            return Response({'detail': 'No puedes agregar productos a un pedido pagado.'}, status=status.HTTP_400_BAD_REQUEST)
        menu_obj, _, _ = menu_del_dia_data(restaurante)
        if not menu_obj:
            return Response({'detail': 'No hay menú del día configurado.'}, status=status.HTTP_400_BAD_REQUEST)

        corr_sopa = (request.data.get('sopa') or '').strip()
        corr_principio = (request.data.get('principio') or '').strip()
        corr_proteina = (request.data.get('proteina') or '').strip()
        corr_acompanante = (request.data.get('acompanante') or '').strip()
        cantidad = int(request.data.get('cantidad') or 1)
        observaciones = (request.data.get('observaciones') or '').strip()

        if cantidad <= 0:
            return Response({'detail': 'La cantidad debe ser mayor que cero.'}, status=status.HTTP_400_BAD_REQUEST)

        categoria_corriente = Categoria.objects.filter(
            nombre__iexact='corriente',
            restaurante=restaurante,
        ).first()
        if not categoria_corriente:
            categoria_corriente = Categoria.objects.create(
                restaurante=restaurante,
                nombre='Corriente',
                activo=True,
            )

        producto, _ = Producto.objects.get_or_create(
            nombre='Menu corriente',
            categoria=categoria_corriente,
            defaults={
                'descripcion': 'Menu del dia',
                'precio': menu_obj.precio_completo,
                'disponible': True,
                'tiempo_preparacion': 15,
            },
        )

        sopa_txt = corr_sopa.strip().lower()
        tiene_sopa = sopa_txt and sopa_txt not in ['sin sopa']
        tiene_otros = any([corr_principio.strip(), corr_proteina.strip(), corr_acompanante.strip()])

        if tiene_sopa and not tiene_otros and getattr(menu_obj, 'precio_sopa', None) is not None:
            precio_unitario = menu_obj.precio_sopa
        elif tiene_sopa:
            precio_unitario = menu_obj.precio_completo
        else:
            precio_unitario = menu_obj.precio_bandeja

        extras = []
        if corr_sopa:
            extras.append(f"Sopa: {corr_sopa}")
        if corr_principio:
            extras.append(f"Principio: {corr_principio}")
        if corr_proteina:
            extras.append(f"Proteina: {corr_proteina}")
        if corr_acompanante:
            extras.append(f"Acompanante: {corr_acompanante}")
        if extras:
            detalle_txt = "\n".join(extras)
            observaciones = f"{observaciones}\n{detalle_txt}".strip() if observaciones else detalle_txt

        consumos_por_unidad = construir_consumos_opciones_menu(
            restaurante,
            'corriente',
            {
                'sopa': corr_sopa,
                'principio': corr_principio,
                'proteina': corr_proteina,
                'acompanante': corr_acompanante,
            },
        )
        errores_stock = validar_stock_consumos(restaurante, consumos_por_unidad, cantidad)
        if errores_stock:
            return Response({'detail': ' '.join(errores_stock)}, status=status.HTTP_400_BAD_REQUEST)

        detalle = DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            observaciones=observaciones,
            consumos_inventario=consumos_por_unidad,
        )
        pedido = _pedido_actualizado(pedido.id)
        return Response(
            {
                'detalle': DetallePedidoSerializer(detalle).data,
                'pedido': PedidoSerializer(pedido, context={'request': request}).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='agregar-desayuno')
    def agregar_desayuno(self, request, pk=None):
        pedido = self.get_object()
        restaurante = getattr(pedido, 'restaurante', None)
        if not caja_abierta(restaurante):
            return Response({'detail': 'La caja está cerrada. No puedes modificar pedidos.'}, status=status.HTTP_400_BAD_REQUEST)
        if hasattr(pedido, 'factura'):
            return Response({'detail': 'No puedes agregar productos a un pedido pagado.'}, status=status.HTTP_400_BAD_REQUEST)
        menu_obj, _, _ = menu_del_dia_data(restaurante)
        if not menu_obj or not menu_obj.precio_desayuno:
            return Response({'detail': 'No hay menú de desayuno configurado.'}, status=status.HTTP_400_BAD_REQUEST)

        des_principal = (request.data.get('principal') or '').strip()
        des_bebida = (request.data.get('bebida') or '').strip()
        des_acompanante = (request.data.get('acompanante') or '').strip()
        cantidad = int(request.data.get('cantidad') or 1)
        observaciones = (request.data.get('observaciones') or '').strip()

        if cantidad <= 0:
            return Response({'detail': 'La cantidad debe ser mayor que cero.'}, status=status.HTTP_400_BAD_REQUEST)

        categoria_desayuno = Categoria.objects.filter(
            nombre__iexact='desayuno',
            restaurante=restaurante,
        ).first()
        if not categoria_desayuno:
            categoria_desayuno = Categoria.objects.create(
                restaurante=restaurante,
                nombre='Desayuno',
                activo=True,
            )

        producto, _ = Producto.objects.get_or_create(
            nombre='Menu desayuno',
            categoria=categoria_desayuno,
            defaults={
                'descripcion': 'Desayuno del dia',
                'precio': menu_obj.precio_desayuno,
                'disponible': True,
                'tiempo_preparacion': 10,
            },
        )

        extras = []
        if des_principal:
            extras.append(f"Desayuno principal: {des_principal}")
        if des_bebida:
            extras.append(f"Bebida: {des_bebida}")
        if des_acompanante:
            extras.append(f"Acompanante desayuno: {des_acompanante}")
        if extras:
            detalle_txt = "\n".join(extras)
            observaciones = f"{observaciones}\n{detalle_txt}".strip() if observaciones else detalle_txt

        consumos_por_unidad = construir_consumos_opciones_menu(
            restaurante,
            'desayuno',
            {
                'principal': des_principal,
                'bebida': des_bebida,
                'acompanante': des_acompanante,
            },
        )
        errores_stock = validar_stock_consumos(restaurante, consumos_por_unidad, cantidad)
        if errores_stock:
            return Response({'detail': ' '.join(errores_stock)}, status=status.HTTP_400_BAD_REQUEST)

        detalle = DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=menu_obj.precio_desayuno,
            observaciones=observaciones,
            consumos_inventario=consumos_por_unidad,
        )
        pedido = _pedido_actualizado(pedido.id)
        return Response(
            {
                'detalle': DetallePedidoSerializer(detalle).data,
                'pedido': PedidoSerializer(pedido, context={'request': request}).data,
            },
            status=status.HTTP_201_CREATED,
        )


class DetallePedidoViewSet(viewsets.ModelViewSet):
    """API para editar y servir detalles de pedidos."""

    serializer_class = DetallePedidoSerializer
    permission_classes = [PedidosPermission]

    def get_queryset(self):
        restaurante = restaurante_usuario(self.request.user)
        if not caja_abierta(restaurante):
            return DetallePedido.objects.none()

        qs = DetallePedido.objects.select_related('pedido', 'producto', 'pedido__mesa')
        if restaurante:
            qs = qs.filter(pedido__restaurante=restaurante)

        pedido_id = self.request.query_params.get('pedido')
        if pedido_id:
            qs = qs.filter(pedido_id=pedido_id)

        servido = self.request.query_params.get('servido')
        if servido in ['1', 'true', 'True']:
            qs = qs.filter(servido=True)
        elif servido in ['0', 'false', 'False']:
            qs = qs.filter(servido=False)

        return qs.order_by('id')

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ActualizarDetallePedidoSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if hasattr(instance.pedido, 'factura'):
            return Response(
                {'detail': 'No puedes editar productos de un pedido pagado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(
            data=request.data,
            partial=partial,
            context={'detalle': instance},
        )
        serializer.is_valid(raise_exception=True)
        detalle = serializer.update(instance, serializer.validated_data)
        return Response(DetallePedidoSerializer(detalle).data)

    def destroy(self, request, *args, **kwargs):
        detalle = self.get_object()
        pedido = detalle.pedido
        if hasattr(pedido, 'factura'):
            return Response(
                {'detail': 'No puedes eliminar productos de un pedido pagado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        response = super().destroy(request, *args, **kwargs)
        pedido.refresh_from_db()
        if not pedido.detalles.exists():
            pedido.calcular_total()
        return response

    @action(detail=True, methods=['post'], url_path='marcar-servido')
    def marcar_servido(self, request, pk=None):
        detalle = self.get_object()
        if hasattr(detalle.pedido, 'factura'):
            return Response(
                {'detail': 'No puedes modificar productos de un pedido pagado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pedido = detalle.pedido
        detalles_pedido = pedido.detalles.all()
        pedido_estaba_listo = detalles_pedido.exists() and all(d.servido for d in detalles_pedido)

        if not detalle.servido:
            detalle.servido = True
            detalle.save(update_fields=['servido'])

        detalles_pedido = pedido.detalles.all()
        pedido_quedo_listo = detalles_pedido.exists() and all(d.servido for d in detalles_pedido)

        if not pedido_estaba_listo and pedido_quedo_listo:
            notificar_mesero_pedido_listo(pedido)

        if pedido_quedo_listo:
            pedido.estado = 'entregado'
            pedido.save(update_fields=['estado'])
            liberar_mesa_si_no_hay_pedidos_activos(pedido.mesa, excluir_pedido_id=pedido.id)

        pedido = _pedido_actualizado(pedido.id)

        return Response(
            {
                'detalle': DetallePedidoSerializer(detalle).data,
                'pedido': PedidoSerializer(pedido, context={'request': request}).data,
            }
        )
