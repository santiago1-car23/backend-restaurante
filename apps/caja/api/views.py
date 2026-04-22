from datetime import datetime

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import localdate
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.caja.models import CajaSesion, Factura, MovimientoCaja
from apps.pedidos.models import Pedido, DetallePedido
from apps.mesas.models import Mesa
from apps.usuarios.models import Empleado
from ..services import archivar_pedidos_y_liberar_mesas
from .serializers import (
    CajaSesionSerializer,
    FacturaSerializer,
    MovimientoCajaSerializer,
    AbrirCajaSerializer,
    CerrarCajaSerializer,
    RegistrarMovimientoSerializer,
    CobrarPedidoSerializer,
)


def _restaurante_de_usuario(user):
    empleado = getattr(user, 'empleado', None)
    return getattr(empleado, 'restaurante', None) if empleado else None


def _usuario_puede_manejar_caja(user):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    empleado = getattr(user, 'empleado', None)
    rol_nombre = getattr(empleado.rol, 'nombre', '') if empleado and empleado.rol else ''
    rol_nombre = rol_nombre.lower()
    return rol_nombre in ('cajero', 'administrador', 'admin', 'gerente')


class IsCajaStaff(permissions.BasePermission):
    """Permite solo a usuarios con rol de caja ver y operar este módulo."""

    def has_permission(self, request, view):
        return _usuario_puede_manejar_caja(request.user)


class CajaSesionViewSet(viewsets.ReadOnlyModelViewSet):
    """Sesiones de caja (historial, detalle y acciones de apertura/cierre)."""

    serializer_class = CajaSesionSerializer
    permission_classes = [permissions.IsAuthenticated, IsCajaStaff]

    def get_queryset(self):
        user = self.request.user
        restaurante = _restaurante_de_usuario(user)
        qs = CajaSesion.objects.all().select_related('usuario_apertura', 'usuario_cierre', 'restaurante')
        if restaurante:
            qs = qs.filter(restaurante=restaurante)

        # Filtros similares a historial_caja
        filtro_desde = self.request.query_params.get('desde') or ''
        filtro_hasta = self.request.query_params.get('hasta') or ''
        filtro_estado = self.request.query_params.get('estado') or 'todas'

        try:
            if filtro_desde:
                desde_dt = datetime.strptime(filtro_desde, '%Y-%m-%d').date()
                qs = qs.filter(fecha_apertura__date__gte=desde_dt)
        except ValueError:
            pass

        try:
            if filtro_hasta:
                hasta_dt = datetime.strptime(filtro_hasta, '%Y-%m-%d').date()
                qs = qs.filter(fecha_apertura__date__lte=hasta_dt)
        except ValueError:
            pass

        if filtro_estado in ('abierta', 'cerrada'):
            qs = qs.filter(estado=filtro_estado)

        return qs

    @action(detail=False, methods=['get'], url_path='activa')
    def activa(self, request):
        """Devuelve la sesión de caja abierta del restaurante del usuario, si existe, con estadísticas básicas."""
        restaurante = _restaurante_de_usuario(request.user)
        sesion_activa = CajaSesion.obtener_activa(restaurante=restaurante) if restaurante else CajaSesion.obtener_activa()

        if not sesion_activa:
            return Response({'sesion': None}, status=status.HTTP_200_OK)

        # Totales muy similares a caja_view
        facturas_qs = sesion_activa.facturas.all()
        from django.db.models import Sum

        total_dia = facturas_qs.aggregate(total=Sum('total'))['total'] or 0
        total_efectivo = facturas_qs.filter(metodo_pago='efectivo').aggregate(total=Sum('total'))['total'] or 0
        total_tarjeta = facturas_qs.filter(metodo_pago='tarjeta').aggregate(total=Sum('total'))['total'] or 0
        total_transferencia = facturas_qs.filter(metodo_pago='transferencia').aggregate(total=Sum('total'))['total'] or 0
        total_nequi = total_transferencia

        total_facturas = facturas_qs.count()
        valor_promedio = (total_dia / total_facturas) if total_facturas > 0 else 0

        saldo_teorico_actual = (
            sesion_activa.saldo_inicial
            + total_efectivo
            + (sesion_activa.entradas_extra or 0)
            - (sesion_activa.salidas or 0)
        )

        # Pedidos para cobrar (mismas reglas que caja_view)
        pedidos_para_cobrar = []
        estados_activos = ['pendiente', 'en_preparacion', 'listo', 'entregado']
        pedidos_qs = (
            Pedido.objects
            .select_related('mesa', 'mesero')
            .filter(
                archivado=False,
                factura__isnull=True,
                estado__in=estados_activos,
            )
            .exclude(mesa__numero=0)
        )
        if restaurante:
            pedidos_qs = pedidos_qs.filter(restaurante=restaurante)

        for p in pedidos_qs:
            pedidos_para_cobrar.append({
                'id': p.id,
                'mesa_numero': p.mesa.numero if p.mesa else None,
                'mesero': p.mesero.get_full_name() if p.mesero else None,
                'total': p.total,
                'estado': p.estado,
            })

        data = {
            'hoy': localdate(),
            'sesion': CajaSesionSerializer(sesion_activa).data,
            'totales': {
                'total_dia': total_dia,
                'total_efectivo': total_efectivo,
                'total_tarjeta': total_tarjeta,
                'total_transferencia': total_transferencia,
                'total_nequi': total_nequi,
                'total_facturas': total_facturas,
                'valor_promedio': valor_promedio,
                'saldo_teorico_actual': saldo_teorico_actual,
            },
            'pedidos_para_cobrar': pedidos_para_cobrar,
        }
        return Response(data)

    @action(detail=False, methods=['post'], url_path='abrir')
    def abrir(self, request):
        """Inicia una nueva sesión de caja (similar a abrir_caja)."""
        serializer = AbrirCajaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        restaurante = _restaurante_de_usuario(request.user)
        sesion_activa = CajaSesion.obtener_activa(restaurante=restaurante) if restaurante else CajaSesion.obtener_activa()
        if sesion_activa:
            return Response({'detail': 'Ya hay una caja abierta actualmente.'}, status=status.HTTP_400_BAD_REQUEST)

        saldo_inicial = serializer.validated_data.get('saldo_inicial') or 0
        observaciones = serializer.validated_data.get('observaciones', '')

        sesion = CajaSesion.objects.create(
            restaurante=restaurante,
            usuario_apertura=request.user,
            saldo_inicial=saldo_inicial,
            observaciones=observaciones,
        )
        return Response(CajaSesionSerializer(sesion).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='cerrar')
    def cerrar(self, request, pk=None):
        """Cierra la sesión de caja activa (similar a cerrar_caja)."""
        sesion = self.get_object()
        if sesion.estado != 'abierta':
            return Response({'detail': 'La sesión ya está cerrada.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CerrarCajaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        salidas_decimal = serializer.validated_data.get('salidas') or 0
        observaciones = serializer.validated_data.get('observaciones', '').strip()

        sesion.salidas = salidas_decimal
        sesion.estado = 'cerrada'
        sesion.fecha_cierre = timezone.now()
        sesion.usuario_cierre = request.user

        if observaciones:
            if sesion.observaciones:
                sesion.observaciones += f"\n{observaciones}"
            else:
                sesion.observaciones = observaciones

        sesion.save()
        archivar_pedidos_y_liberar_mesas(_restaurante_de_usuario(request.user))

        return Response(CajaSesionSerializer(sesion).data)

    @action(detail=True, methods=['get'], url_path='resumen')
    def resumen(self, request, pk=None):
        """Resumen detallado de una sesión de caja (similar a resumen_caja)."""
        sesion = self.get_object()
        facturas_sesion = sesion.facturas.all()
        movimientos_sesion = sesion.movimientos.all()
        from django.db.models import Sum

        total_facturas_monto = facturas_sesion.aggregate(total=Sum('total'))['total'] or 0
        total_efectivo = facturas_sesion.filter(metodo_pago='efectivo').aggregate(total=Sum('total'))['total'] or 0
        total_tarjeta = facturas_sesion.filter(metodo_pago='tarjeta').aggregate(total=Sum('total'))['total'] or 0
        total_transferencia = facturas_sesion.filter(metodo_pago='transferencia').aggregate(total=Sum('total'))['total'] or 0
        total_mixto = facturas_sesion.filter(metodo_pago='mixto').aggregate(total=Sum('total'))['total'] or 0

        top_productos = (
            DetallePedido.objects
            .filter(pedido__factura__sesion=sesion)
            .values('producto__nombre')
            .annotate(cantidad=Sum('cantidad'), total=Sum('subtotal'))
            .order_by('-cantidad')
        )

        total_facturas = facturas_sesion.count()
        ticket_promedio = (total_facturas_monto / total_facturas) if total_facturas > 0 else 0
        resultado_neto = (
            total_facturas_monto
            + (sesion.entradas_extra or 0)
            - (sesion.salidas or 0)
        )

        data = {
            'sesion': CajaSesionSerializer(sesion).data,
            'facturas': FacturaSerializer(facturas_sesion, many=True).data,
            'movimientos': MovimientoCajaSerializer(movimientos_sesion, many=True).data,
            'total_facturas_monto': total_facturas_monto,
            'total_facturas': total_facturas,
            'ticket_promedio': ticket_promedio,
            'total_efectivo': total_efectivo,
            'total_tarjeta': total_tarjeta,
            'total_transferencia': total_transferencia,
            'total_mixto': total_mixto,
            'resultado_neto': resultado_neto,
            'top_productos': list(top_productos),
        }
        return Response(data)

    @action(detail=True, methods=['post'], url_path='registrar-entrada')
    def registrar_entrada(self, request, pk=None):
        """Entrada extra de dinero a la sesión (similar a registrar_entrada)."""
        sesion = self.get_object()
        if sesion.estado != 'abierta':
            return Response({'detail': 'La sesión no está abierta.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegistrarMovimientoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        valor_decimal = serializer.validated_data['valor']
        descripcion = serializer.validated_data.get('descripcion', '').strip()

        if valor_decimal <= 0:
            return Response({'detail': 'Ingresa un valor de entrada mayor que cero.'}, status=status.HTTP_400_BAD_REQUEST)

        sesion.entradas_extra = (sesion.entradas_extra or 0) + valor_decimal

        MovimientoCaja.objects.create(
            sesion=sesion,
            tipo='entrada',
            monto=valor_decimal,
            concepto=descripcion or 'Entrada adicional',
            usuario=request.user if request.user.is_authenticated else None,
        )

        if descripcion:
            texto = f"Entrada extra: ${valor_decimal} - {descripcion}"
            if sesion.observaciones:
                sesion.observaciones += f"\n{texto}"
            else:
                sesion.observaciones = texto

        sesion.save()
        return Response(CajaSesionSerializer(sesion).data)

    @action(detail=True, methods=['post'], url_path='registrar-salida')
    def registrar_salida(self, request, pk=None):
        """Salida de caja (similar a registrar_salida)."""
        sesion = self.get_object()
        if sesion.estado != 'abierta':
            return Response({'detail': 'La sesión no está abierta.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegistrarMovimientoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        valor_decimal = serializer.validated_data['valor']
        descripcion = serializer.validated_data.get('descripcion', '').strip()

        if valor_decimal <= 0:
            return Response({'detail': 'Ingresa un valor de salida mayor que cero.'}, status=status.HTTP_400_BAD_REQUEST)

        sesion.salidas = (sesion.salidas or 0) + valor_decimal

        MovimientoCaja.objects.create(
            sesion=sesion,
            tipo='salida',
            monto=valor_decimal,
            concepto=descripcion or 'Salida de caja',
            usuario=request.user if request.user.is_authenticated else None,
        )

        if descripcion:
            texto = f"Salida: ${valor_decimal} - {descripcion}"
            if sesion.observaciones:
                sesion.observaciones += f"\n{texto}"
            else:
                sesion.observaciones = texto

        sesion.save()
        return Response(CajaSesionSerializer(sesion).data)


class FacturaViewSet(viewsets.ReadOnlyModelViewSet):
    """Consulta de facturas y acción para cobrar pedidos (crear factura)."""

    serializer_class = FacturaSerializer
    permission_classes = [permissions.IsAuthenticated, IsCajaStaff]

    def get_queryset(self):
        user = self.request.user
        restaurante = _restaurante_de_usuario(user)
        qs = Factura.objects.select_related('pedido__mesa', 'cajero')
        if restaurante:
            qs = qs.filter(pedido__restaurante=restaurante)
        return qs

    @action(detail=False, methods=['post'], url_path='cobrar-pedido')
    def cobrar_pedido(self, request):
        """Genera una factura para un pedido usando la caja activa (similar a views.cobrar_pedido)."""
        serializer = CobrarPedidoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pedido_id = serializer.validated_data['pedido_id']
        metodo_pago = serializer.validated_data['metodo_pago']
        cliente_nombre = serializer.validated_data.get('cliente_nombre', '').strip()
        cliente_nit = serializer.validated_data.get('cliente_nit', '').strip()

        restaurante = _restaurante_de_usuario(request.user)
        if restaurante:
            pedido = get_object_or_404(Pedido, pk=pedido_id, restaurante=restaurante)
        else:
            pedido = get_object_or_404(Pedido, pk=pedido_id)

        # Ya facturado
        if hasattr(pedido, 'factura'):
            factura = pedido.factura
            return Response(FacturaSerializer(factura).data, status=status.HTTP_200_OK)

        sesion_actual = CajaSesion.obtener_activa(restaurante=restaurante) if restaurante else CajaSesion.obtener_activa()
        if not sesion_actual:
            return Response({'detail': 'Debe abrir la caja antes de poder cobrar.'}, status=status.HTTP_400_BAD_REQUEST)

        # Nos aseguramos de que el total del pedido esté calculado
        detalles_pedido = list(pedido.detalles.select_related('producto').all())
        total_pedido = pedido.calcular_total()

        factura = Factura.objects.create(
            pedido=pedido,
            sesion=sesion_actual,
            cajero=request.user,
            metodo_pago=metodo_pago,
            subtotal=total_pedido,
            impuesto=0,
            descuento=0,
            total=total_pedido,
            cliente_nombre=cliente_nombre,
            cliente_nit=cliente_nit,
        )

        # El inventario ya se descuenta al crear/editar/eliminar detalles del pedido.
        # En caja solo facturamos para evitar duplicar salidas de inventario.

        # Si el pedido es venta rápida (extra), registrar movimiento informativo
        if getattr(pedido, 'es_extra', False):
            MovimientoCaja.objects.create(
                sesion=sesion_actual,
                tipo='entrada',
                monto=total_pedido,
                concepto=f'Venta rápida (productos: {", ".join([d.producto.nombre for d in pedido.detalles.all()])})',
                usuario=request.user,
            )

        pedido.estado = 'entregado'
        pedido.save(update_fields=['estado'])

        mesa = pedido.mesa
        if mesa:
            estados_activos = ['pendiente', 'en_preparacion', 'listo']
            hay_otro_activo = mesa.pedidos.filter(
                archivado=False,
                estado__in=estados_activos,
            ).exclude(id=pedido.id).exists()
            if not hay_otro_activo:
                mesa.estado = 'libre'
                mesa.save(update_fields=['estado'])

        return Response(FacturaSerializer(factura).data, status=status.HTTP_201_CREATED)


class MovimientoCajaViewSet(viewsets.ReadOnlyModelViewSet):
    """Listado de movimientos de caja (entradas/salidas)."""

    serializer_class = MovimientoCajaSerializer
    permission_classes = [permissions.IsAuthenticated, IsCajaStaff]

    def get_queryset(self):
        user = self.request.user
        restaurante = _restaurante_de_usuario(user)
        qs = MovimientoCaja.objects.select_related('sesion', 'usuario')
        if restaurante:
            qs = qs.filter(sesion__restaurante=restaurante)
        return qs
