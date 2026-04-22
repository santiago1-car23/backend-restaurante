from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from django.utils.timezone import localdate

from apps.pedidos.models import Pedido, DetallePedido
from apps.mesas.models import Mesa
from .models import Factura, CajaSesion, MovimientoCaja
from .services import archivar_pedidos_y_liberar_mesas


def _usuario_puede_manejar_caja(user):
    """Define qué usuarios pueden abrir/cerrar caja y cobrar.

    Por defecto: staff de Django o roles personalizados de tipo cajero/admin.
    """
    if not user.is_authenticated:
        return False

    if user.is_staff:
        return True

    empleado = getattr(user, 'empleado', None)
    rol_nombre = getattr(empleado.rol, 'nombre', '') if empleado and empleado.rol else ''
    rol_nombre = rol_nombre.lower()
    return rol_nombre in ('cajero', 'administrador', 'admin', 'gerente')


def _restaurante_de_usuario(user):
    """Obtiene el restaurante asociado al empleado del usuario, si existe."""
    empleado = getattr(user, 'empleado', None)
    return getattr(empleado, 'restaurante', None) if empleado else None


@login_required(login_url='login')
def caja_view(request):
    """Vista principal de Caja: muestra la sesión activa y sus estadísticas.

    Si no hay sesión abierta, se muestran todos los totales en cero,
    pero las facturas y sesiones anteriores quedan guardadas en la base de datos.
    """
    hoy = localdate()

    restaurante = _restaurante_de_usuario(request.user)
    sesion_activa = CajaSesion.obtener_activa(restaurante=restaurante) if restaurante else CajaSesion.obtener_activa()

    if sesion_activa:
        facturas_qs = Factura.objects.filter(sesion=sesion_activa)
    else:
        facturas_qs = Factura.objects.none()

    total_dia = facturas_qs.aggregate(total=Sum('total'))['total'] or 0
    total_efectivo = facturas_qs.filter(metodo_pago='efectivo').aggregate(total=Sum('total'))['total'] or 0
    total_tarjeta = facturas_qs.filter(metodo_pago='tarjeta').aggregate(total=Sum('total'))['total'] or 0
    # Internamente sigue siendo "transferencia", pero en la interfaz se muestra como Nequi
    total_transferencia = facturas_qs.filter(metodo_pago='transferencia').aggregate(total=Sum('total'))['total'] or 0
    total_nequi = total_transferencia

    # Estadísticas sencillas de ventas de la sesión
    total_facturas = facturas_qs.count()
    valor_promedio = (total_dia / total_facturas) if total_facturas > 0 else 0

    # Saldo teórico actual de EFECTIVO en caja (solo si hay sesión abierta)
    saldo_teorico_actual = None
    if sesion_activa:
        saldo_teorico_actual = (
            sesion_activa.saldo_inicial
            + total_efectivo
            + (sesion_activa.entradas_extra or 0)
            - (sesion_activa.salidas or 0)
        )

    # Top productos vendidos (por cantidad) según detalles de pedidos facturados en la sesión
    if sesion_activa:
        top_productos = (
            DetallePedido.objects
            .filter(pedido__factura__sesion=sesion_activa)
            .values('producto__nombre')
            .annotate(cantidad=Sum('cantidad'), total=Sum('subtotal'))
            .order_by('-cantidad')[:5]
        )
    else:
        top_productos = []

    # Pedidos asociados a mesas físicas que aún no tienen factura (mesas ocupadas para cobrar)
    pedidos_para_cobrar = []
    if sesion_activa:
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

        pedidos_para_cobrar = list(pedidos_qs)

    context = {
        'hoy': hoy,
        'facturas': facturas_qs,
        'total_dia': total_dia,
        'total_efectivo': total_efectivo,
        'total_tarjeta': total_tarjeta,
        'total_transferencia': total_transferencia,
        'total_nequi': total_nequi,
        'total_facturas': total_facturas,
        'valor_promedio': valor_promedio,
        'top_productos': top_productos,
        'pedidos_para_cobrar': pedidos_para_cobrar,
        'sesion_activa': sesion_activa,
        'saldo_teorico_actual': saldo_teorico_actual,
    }

    return render(request, 'caja/caja.html', context)


@login_required(login_url='login')
def registrar_salida(request):
    """Registra una salida de caja (gasto/retiro) sumándola a la sesión activa."""
    if not _usuario_puede_manejar_caja(request.user):
        messages.error(request, 'No tienes permisos para manejar la caja.')
        return redirect('dashboard')

    restaurante = _restaurante_de_usuario(request.user)
    sesion_actual = CajaSesion.obtener_activa(restaurante=restaurante) if restaurante else CajaSesion.obtener_activa()
    if not sesion_actual:
        messages.error(request, 'No hay una caja abierta para registrar salidas.')
        return redirect('caja:index')

    if request.method == 'POST':
        valor = request.POST.get('valor') or '0'
        descripcion = request.POST.get('descripcion', '').strip()

        from decimal import Decimal
        try:
            valor_decimal = Decimal(valor)
        except Exception:
            valor_decimal = 0

        if valor_decimal <= 0:
            messages.error(request, 'Ingresa un valor de salida mayor que cero.')
            return redirect('caja:index')

        sesion_actual.salidas = (sesion_actual.salidas or 0) + valor_decimal

        # Registrar movimiento detallado de salida
        MovimientoCaja.objects.create(
            sesion=sesion_actual,
            tipo='salida',
            monto=valor_decimal,
            concepto=descripcion or 'Salida de caja',
            usuario=request.user if request.user.is_authenticated else None,
        )

        if descripcion:
            texto = f"Salida: ${valor_decimal} - {descripcion}"
            if sesion_actual.observaciones:
                sesion_actual.observaciones += f"\n{texto}"
            else:
                sesion_actual.observaciones = texto

        sesion_actual.save()
        messages.success(request, 'Salida registrada en la caja actual.')

    return redirect('caja:index')


@login_required(login_url='login')
def registrar_entrada(request):
    """Registra una entrada extra de dinero a la caja actual.

    Pensado para ingresos que no salen de las facturas normales: ventas por aparte,
    recargas, etc. Se suman al campo entradas_extra de la sesión activa.
    """
    if not _usuario_puede_manejar_caja(request.user):
        messages.error(request, 'No tienes permisos para manejar la caja.')
        return redirect('dashboard')

    restaurante = _restaurante_de_usuario(request.user)
    sesion_actual = CajaSesion.obtener_activa(restaurante=restaurante) if restaurante else CajaSesion.obtener_activa()
    if not sesion_actual:
        messages.error(request, 'No hay una caja abierta para registrar entradas.')
        return redirect('caja:index')

    if request.method == 'POST':
        from decimal import Decimal

        valor = request.POST.get('valor') or '0'
        descripcion = request.POST.get('descripcion', '').strip()

        try:
            valor_decimal = Decimal(valor)
        except Exception:
            valor_decimal = Decimal('0')

        if valor_decimal <= 0:
            messages.error(request, 'Ingresa un valor de entrada mayor que cero.')
            return redirect('caja:index')

        sesion_actual.entradas_extra = (sesion_actual.entradas_extra or 0) + valor_decimal

        MovimientoCaja.objects.create(
            sesion=sesion_actual,
            tipo='entrada',
            monto=valor_decimal,
            concepto=descripcion or 'Entrada adicional',
            usuario=request.user if request.user.is_authenticated else None,
        )

        if descripcion:
            texto = f"Entrada extra: ${valor_decimal} - {descripcion}"
            if sesion_actual.observaciones:
                sesion_actual.observaciones += f"\n{texto}"
            else:
                sesion_actual.observaciones = texto

        sesion_actual.save()
        messages.success(request, 'Entrada adicional registrada en la caja actual.')

    return redirect('caja:index')


@login_required(login_url='login')
def venta_rapida(request):
    """Venta rápida SIN mesa física reutilizando la pantalla de detalle de pedido.

    Crea (o reutiliza) un Pedido asociado a una mesa virtual número 0 y redirige al
    detalle del pedido para que allí se agreguen los productos como siempre.
    """
    if not _usuario_puede_manejar_caja(request.user):
        messages.error(request, 'No tienes permisos para manejar la caja.')
        return redirect('dashboard')

    restaurante = _restaurante_de_usuario(request.user)
    sesion_actual = CajaSesion.obtener_activa(restaurante=restaurante) if restaurante else CajaSesion.obtener_activa()
    if not sesion_actual:
        messages.error(request, 'No hay una caja abierta para registrar ventas rápidas.')
        return redirect('caja:index')

    # Mesa virtual para ventas rápidas
    mesa_rapida, _ = Mesa.objects.get_or_create(
        restaurante=restaurante,
        numero=0,
        defaults={
            'capacidad': 1,
            'estado': 'libre',
            'ubicacion': 'VENTA RÁPIDA',
            'activa': False,
        },
    )

    # Pedido vigente de venta rápida (no archivado ni facturado)
    pedido = (
        Pedido.objects
        .filter(mesa=mesa_rapida, archivado=False, factura__isnull=True)
        .order_by('-fecha_creacion')
        .first()
    )
    if not pedido:
        pedido = Pedido.objects.create(
            restaurante=restaurante,
            mesa=mesa_rapida,
            mesero=request.user,
            estado='pendiente',
            observaciones='Venta rápida sin mesa',
        )

    return redirect('pedidos:detalle', pedido.id)


@login_required(login_url='login')
def abrir_caja(request):
    """Inicia una nueva sesión de caja si no hay una abierta."""
    if not _usuario_puede_manejar_caja(request.user):
        messages.error(request, 'No tienes permisos para manejar la caja.')
        return redirect('dashboard')

    restaurante = _restaurante_de_usuario(request.user)
    sesion_activa = CajaSesion.obtener_activa(restaurante=restaurante) if restaurante else CajaSesion.obtener_activa()
    if sesion_activa:
        messages.info(request, 'Ya hay una caja abierta actualmente.')
        return redirect('caja:index')

    if request.method == 'POST':
        saldo_inicial_str = request.POST.get('saldo_inicial') or '0'
        observaciones = request.POST.get('observaciones', '').strip()

        from decimal import Decimal
        try:
            saldo_inicial = Decimal(saldo_inicial_str)
        except Exception:
            saldo_inicial = Decimal('0')

        CajaSesion.objects.create(
            restaurante=restaurante,
            usuario_apertura=request.user,
            saldo_inicial=saldo_inicial,
            observaciones=observaciones,
        )

        messages.success(request, 'Sesión de caja abierta correctamente.')
        return redirect('caja:index')

    contexto = {
        'today': localdate(),
    }
    return render(request, 'caja/abrir_caja.html', contexto)


@login_required(login_url='login')
def cerrar_caja(request):
    """Cierra la sesión de caja activa y muestra un resumen previo al cierre."""
    if not _usuario_puede_manejar_caja(request.user):
        messages.error(request, 'No tienes permisos para manejar la caja.')
        return redirect('dashboard')

    restaurante = _restaurante_de_usuario(request.user)
    sesion_actual = CajaSesion.obtener_activa(restaurante=restaurante) if restaurante else CajaSesion.obtener_activa()
    if not sesion_actual:
        messages.error(request, 'No hay una caja abierta para cerrar.')
        return redirect('caja:index')

    # Facturas asociadas a la sesión, para estadística de cierre
    facturas_sesion = sesion_actual.facturas.all()
    total_facturas_monto = facturas_sesion.aggregate(total=Sum('total'))['total'] or 0
    total_efectivo = facturas_sesion.filter(metodo_pago='efectivo').aggregate(total=Sum('total'))['total'] or 0
    total_tarjeta = facturas_sesion.filter(metodo_pago='tarjeta').aggregate(total=Sum('total'))['total'] or 0
    total_transferencia = facturas_sesion.filter(metodo_pago='transferencia').aggregate(total=Sum('total'))['total'] or 0
    total_mixto = facturas_sesion.filter(metodo_pago='mixto').aggregate(total=Sum('total'))['total'] or 0

    if request.method == 'POST':
        # Permitir registrar salidas y observaciones al cerrar
        salidas_input = request.POST.get('salidas') or '0'
        observaciones = request.POST.get('observaciones', '').strip()

        from decimal import Decimal
        try:
            salidas_decimal = Decimal(salidas_input)
        except Exception:
            salidas_decimal = 0

        sesion_actual.salidas = salidas_decimal
        sesion_actual.estado = 'cerrada'
        sesion_actual.fecha_cierre = timezone.now()
        sesion_actual.usuario_cierre = request.user

        if observaciones:
            if sesion_actual.observaciones:
                sesion_actual.observaciones += f"\n{observaciones}"
            else:
                sesion_actual.observaciones = observaciones

        sesion_actual.save()
        archivar_pedidos_y_liberar_mesas(restaurante)

        messages.success(request, 'Caja cerrada correctamente.')
        return redirect('caja:resumen_caja', sesion_id=sesion_actual.id)

    contexto = {
        'sesion': sesion_actual,
        'total_facturas': total_facturas_monto,
        'total_efectivo': total_efectivo,
        'total_tarjeta': total_tarjeta,
        'total_transferencia': total_transferencia,
        'total_mixto': total_mixto,
    }
    return render(request, 'caja/cerrar_caja.html', contexto)


@login_required(login_url='login')
def resumen_caja(request, sesion_id):
    """Muestra el resumen completo de una sesión de caja cerrada."""
    restaurante = _restaurante_de_usuario(request.user)

    sesiones_qs = CajaSesion.objects.all()
    # Si el usuario pertenece a un restaurante específico, limitar a ese restaurante
    # incluso si es superusuario (para que no vea datos mezclados si está asignado a uno)
    if restaurante:
        sesiones_qs = sesiones_qs.filter(restaurante=restaurante)

    sesion = get_object_or_404(sesiones_qs, pk=sesion_id)

    facturas_sesion = sesion.facturas.all()
    movimientos_sesion = sesion.movimientos.all()
    total_facturas_monto = facturas_sesion.aggregate(total=Sum('total'))['total'] or 0
    total_efectivo = facturas_sesion.filter(metodo_pago='efectivo').aggregate(total=Sum('total'))['total'] or 0
    total_tarjeta = facturas_sesion.filter(metodo_pago='tarjeta').aggregate(total=Sum('total'))['total'] or 0
    total_transferencia = facturas_sesion.filter(metodo_pago='transferencia').aggregate(total=Sum('total'))['total'] or 0
    total_mixto = facturas_sesion.filter(metodo_pago='mixto').aggregate(total=Sum('total'))['total'] or 0

    # Productos vendidos en la sesión (todos los productos del día)
    top_productos = (
        DetallePedido.objects
        .filter(pedido__factura__sesion=sesion)
        .values('producto__nombre')
        .annotate(cantidad=Sum('cantidad'), total=Sum('subtotal'))
        .order_by('-cantidad')
    )

    total_facturas = facturas_sesion.count()
    ticket_promedio = (total_facturas_monto / total_facturas) if total_facturas > 0 else 0
    # Resultado del día: total facturado + entradas adicionales - salidas
    resultado_neto = (
        total_facturas_monto
        + (sesion.entradas_extra or 0)
        - (sesion.salidas or 0)
    )

    contexto = {
        'sesion': sesion,
        'facturas': facturas_sesion,
        'movimientos': movimientos_sesion,
        'total_facturas_monto': total_facturas_monto,
        'total_facturas': total_facturas,
        'ticket_promedio': ticket_promedio,
        'total_efectivo': total_efectivo,
        'total_tarjeta': total_tarjeta,
        'total_transferencia': total_transferencia,
        'total_mixto': total_mixto,
        'resultado_neto': resultado_neto,
        'top_productos': top_productos,
    }
    return render(request, 'caja/resumen_caja.html', contexto)


@login_required(login_url='login')
def historial_caja(request):
    """Listado de todas las sesiones de caja con acceso a su resumen."""
    if not _usuario_puede_manejar_caja(request.user):
        messages.error(request, 'No tienes permisos para ver el historial de caja.')
        return redirect('dashboard')

    restaurante = _restaurante_de_usuario(request.user)

    sesiones = (
        CajaSesion.objects
        .select_related('usuario_apertura', 'usuario_cierre')
        .order_by('-fecha_apertura')
    )

    # Si el usuario tiene restaurante asignado, filtrar por él (aunque sea superuser)
    if restaurante:
        sesiones = sesiones.filter(restaurante=restaurante)

    # Filtros simples por fecha y estado para facilitar la consulta
    filtro_desde = request.GET.get('desde') or ''
    filtro_hasta = request.GET.get('hasta') or ''
    filtro_estado = request.GET.get('estado') or 'todas'

    try:
        if filtro_desde:
            desde_dt = datetime.strptime(filtro_desde, '%Y-%m-%d').date()
            sesiones = sesiones.filter(fecha_apertura__date__gte=desde_dt)
    except ValueError:
        filtro_desde = ''  # Ignorar formato inválido

    try:
        if filtro_hasta:
            hasta_dt = datetime.strptime(filtro_hasta, '%Y-%m-%d').date()
            sesiones = sesiones.filter(fecha_apertura__date__lte=hasta_dt)
    except ValueError:
        filtro_hasta = ''

    if filtro_estado in ('abierta', 'cerrada'):
        sesiones = sesiones.filter(estado=filtro_estado)
    else:
        filtro_estado = 'todas'

    contexto = {
        'sesiones': sesiones,
        'filtro_desde': filtro_desde,
        'filtro_hasta': filtro_hasta,
        'filtro_estado': filtro_estado,
    }
    return render(request, 'caja/historial_caja.html', contexto)


@login_required(login_url='login')
def cobrar_pedido(request, pedido_id):
    """Genera una factura para un pedido (mesa) usando la caja activa."""
    if not _usuario_puede_manejar_caja(request.user):
        messages.error(request, 'No tienes permisos para cobrar pedidos en caja.')
        return redirect('pedidos:lista')
    restaurante = _restaurante_de_usuario(request.user)

    if restaurante:
        pedido = get_object_or_404(Pedido, pk=pedido_id, restaurante=restaurante)
    else:
        pedido = get_object_or_404(Pedido, pk=pedido_id)

    # Si ya está facturado, no duplicar
    if hasattr(pedido, 'factura'):
        messages.info(request, f'El pedido #{pedido.id} ya tiene una factura.')
        return redirect('caja:index')

    sesion_actual = CajaSesion.obtener_activa(restaurante=restaurante) if restaurante else CajaSesion.obtener_activa()
    if not sesion_actual:
        messages.error(request, 'Debe abrir la caja antes de poder cobrar.')
        return redirect('caja:index')

    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        cliente_nombre = request.POST.get('cliente_nombre', '').strip()
        cliente_nit = request.POST.get('cliente_nit', '').strip()

        if metodo_pago not in dict(Factura.METODOS_PAGO):
            messages.error(request, 'Seleccione un método de pago válido.')
            return redirect('caja:cobrar_pedido', pedido_id=pedido.id)

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
            from .models import MovimientoCaja
            MovimientoCaja.objects.create(
                sesion=sesion_actual,
                tipo='entrada',
                monto=total_pedido,
                concepto=f'Venta rápida (productos: {", ".join([d.producto.nombre for d in pedido.detalles.all()])})',
                usuario=request.user,
            )

        # Marcar pedido como entregado
        pedido.estado = 'entregado'
        pedido.save(update_fields=['estado'])

        mesa = pedido.mesa
        # Liberar mesa solo si no quedan pedidos activos (pendiente / en_preparacion / listo)
        if mesa:
            from apps.pedidos.models import Pedido as PedidoModel
            estados_activos = ['pendiente', 'en_preparacion', 'listo']
            hay_otro_activo = mesa.pedidos.filter(
                archivado=False,
                estado__in=estados_activos,
            ).exclude(id=pedido.id).exists()
            if not hay_otro_activo:
                mesa.estado = 'libre'
                mesa.save(update_fields=['estado'])

        messages.success(request, f'Factura {factura.numero_factura} creada correctamente.')
        # Después de cobrar, ir directo a ver/imprimir la factura
        return redirect('caja:factura_detalle', factura_id=factura.id)

    contexto = {
        'pedido': pedido,
    }
    return render(request, 'caja/cobrar_pedido.html', contexto)


@login_required(login_url='login')
def factura_detalle(request, factura_id):
    """Muestra el detalle de una factura específica (una por pedido)."""
    restaurante = _restaurante_de_usuario(request.user)

    facturas_qs = Factura.objects.select_related('pedido__mesa', 'cajero')
    if restaurante:
        facturas_qs = facturas_qs.filter(pedido__restaurante=restaurante)

    factura = get_object_or_404(facturas_qs, pk=factura_id)
    detalles = factura.pedido.detalles.select_related('producto').all()

    contexto = {
        'factura': factura,
        'pedido': factura.pedido,
        'detalles': detalles,
    }
    return render(request, 'caja/factura_detalle.html', contexto)
