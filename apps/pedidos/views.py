from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.template.loader import render_to_string

from apps.mesas.models import Mesa
from apps.menu.inventario import (
    construir_consumos_opciones_menu,
    construir_consumos_receta_producto,
    validar_stock_consumos,
)
from apps.menu.models import Producto, Categoria
from apps.inventario.models import Ingrediente
from apps.caja.models import Factura
from .models import Pedido, DetallePedido
from .services import (
    ESTADOS_PEDIDO_ACTIVOS,
    caja_abierta,
    get_empleado_rol_restaurante,
    liberar_mesa_si_no_hay_pedidos_activos,
    menu_del_dia_data,
    notificar_mesero_pedido_listo,
)

PRODUCTOS_TECNICOS_MENU = ['Menu corriente', 'Menu desayuno']


@login_required(login_url='login')
def lista_pedidos(request):
    _, rol_nombre, restaurante = get_empleado_rol_restaurante(request.user)
    caja_abierta_actual = caja_abierta(restaurante)

    # Crear nueva orden si se envía POST
    if request.method == 'POST':
        if not caja_abierta_actual:
            messages.warning(request, 'La caja está cerrada. Debes abrir la caja para gestionar pedidos.')
            return redirect('pedidos:lista')

        mesa_id = request.POST.get('mesa')
        if mesa_id:
            try:
                mesa = Mesa.objects.get(pk=mesa_id, activa=True)
            except Mesa.DoesNotExist:
                return redirect('pedidos:lista')

            # Proteger por restaurante: no permitir abrir pedido en mesa de otro restaurante
            if restaurante and mesa.restaurante_id != getattr(restaurante, 'id', None):
                return redirect('pedidos:lista')

            if mesa.estado == 'libre':
                pedido = Pedido.objects.create(
                    mesa=mesa,
                    mesero=request.user,
                    restaurante=mesa.restaurante,
                    estado='pendiente',
                )
                mesa.estado = 'ocupada'
                mesa.save(update_fields=['estado'])
                return redirect('pedidos:detalle', orden_id=pedido.id)

    # Pedidos activos para el panel: todos los que no estén cancelados y no
    # hayan sido archivados (cerrados en caja).
    ordenes_qs = Pedido.objects.none()
    if caja_abierta_actual:
        ordenes_qs = Pedido.objects.select_related('mesa', 'mesero').filter(
            archivado=False,
        ).exclude(
            estado='cancelado',
        ).order_by('-fecha_creacion')

    # Separar por restaurante: cada usuario ve solo pedidos de su restaurante.
    if restaurante:
        ordenes_qs = ordenes_qs.filter(restaurante=restaurante)

    mesas_qs = Mesa.objects.none()
    if caja_abierta_actual:
        mesas_qs = Mesa.objects.filter(activa=True)
        if restaurante:
            mesas_qs = mesas_qs.filter(restaurante=restaurante)

    contexto = {
        'ordenes': ordenes_qs,
        'mesas': mesas_qs,
        'rol_nombre': rol_nombre,
        'caja_abierta': caja_abierta_actual,
    }
    return render(request, 'pedidos/pedidos_list.html', contexto)


@login_required(login_url='login')
def lista_pedidos_json(request):
    _, _, restaurante = get_empleado_rol_restaurante(request.user)
    if not caja_abierta(restaurante):
        return JsonResponse({'ordenes': []})

    pedidos_qs = Pedido.objects.select_related('mesa', 'mesero').filter(
        archivado=False,
    ).exclude(
        estado='cancelado',
    ).order_by('-fecha_creacion')

    # JSON también separado por restaurante.
    if restaurante:
        pedidos_qs = pedidos_qs.filter(restaurante=restaurante)


    data = []
    for pedido in pedidos_qs:
        mesa = pedido.mesa
        mesero = pedido.mesero

        if mesero:
            nombre = mesero.get_full_name()
            mesero_nombre = nombre if nombre else mesero.username
        else:
            mesero_nombre = ''

        # Para OneToOne, hasattr no sirve porque lanza DoesNotExist;
        # usamos un try/except para detectarla de forma segura.
        try:
            _ = pedido.factura
            tiene_factura = True
        except Factura.DoesNotExist:
            tiene_factura = False

        data.append({
            'id': pedido.id,
            'mesa_numero': mesa.numero if mesa else None,
            'mesero_nombre': mesero_nombre,
            'estado': pedido.estado,
            'estado_display': pedido.get_estado_display(),
            'total': float(pedido.total or 0),
            'hora': pedido.fecha_creacion.strftime('%H:%M') if pedido.fecha_creacion else '',
            'tiene_factura': tiene_factura,
        })

    return JsonResponse({'ordenes': data})


@login_required(login_url='login')
def detalle_pedido(request, orden_id):
    pedido = get_object_or_404(Pedido, pk=orden_id)
    _, rol_nombre, _ = get_empleado_rol_restaurante(request.user)
    restaurante = getattr(pedido, 'restaurante', None)
    if not caja_abierta(restaurante):
        messages.warning(request, 'La caja está cerrada. No puedes gestionar pedidos.')
        return redirect('pedidos:lista')

    menu_obj, menu_corriente_data, menu_desayuno_data = menu_del_dia_data(restaurante)

    categoria_id = request.GET.get('categoria')
    query = (request.GET.get('q') or '').strip()
    show_corriente = request.GET.get('corriente') == '1'
    show_desayuno = request.GET.get('desayuno') == '1'

    if request.method == 'POST':
        # Cocinero solo puede ver detalle (y marcar servido en otra vista), no agregar productos
        if rol_nombre == 'cocinero':
            return redirect('pedidos:detalle', orden_id=pedido.id)

        tipo_form = request.POST.get('tipo_form', 'general')
        producto_id = request.POST.get('producto')
        cantidad = request.POST.get('cantidad') or 1
        observaciones = request.POST.get('observaciones', '').strip()

        # Campos extra cuando se agrega un "corriente"
        corr_sopa = request.POST.get('corr_sopa', '').strip()
        corr_principio = request.POST.get('corr_principio', '').strip()
        corr_proteina = request.POST.get('corr_proteina', '').strip()
        corr_acompanante = request.POST.get('corr_acompanante', '').strip()
        # Campos extra cuando se agrega un desayuno
        des_principal = request.POST.get('des_principal', '').strip()
        des_bebida = request.POST.get('des_bebida', '').strip()
        des_acompanante = request.POST.get('des_acompanante', '').strip()

        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            cantidad = 1

        if cantidad > 0:
            # Formulario GENERAL: usa el producto escogido normalmente
            if tipo_form == 'general' and producto_id:
                producto = get_object_or_404(Producto, pk=producto_id, disponible=True)
                precio_unitario = producto.precio

            # Formulario CORRIENTE: producto especial "Menu corriente"
            elif tipo_form == 'corriente' and menu_obj:
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
                    if observaciones:
                        observaciones = f"{observaciones}\n{detalle_txt}"
                    else:
                        observaciones = detalle_txt

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
                    }
                )

                sopa_txt = (corr_sopa or '').strip().lower()
                tiene_sopa = sopa_txt and sopa_txt not in ['sin sopa']
                tiene_otros = any([
                    (corr_principio or '').strip(),
                    (corr_proteina or '').strip(),
                    (corr_acompanante or '').strip(),
                ])

                if tiene_sopa and not tiene_otros and getattr(menu_obj, 'precio_sopa', None) is not None:
                    precio_unitario = menu_obj.precio_sopa
                elif tiene_sopa:
                    precio_unitario = menu_obj.precio_completo
                else:
                    precio_unitario = menu_obj.precio_bandeja

            # Formulario DESAYUNO
            elif tipo_form == 'desayuno' and menu_obj and menu_desayuno_data:
                extras = []
                if des_principal:
                    extras.append(f"Desayuno principal: {des_principal}")
                if des_bebida:
                    extras.append(f"Bebida: {des_bebida}")
                if des_acompanante:
                    extras.append(f"Acompanante desayuno: {des_acompanante}")
                if extras:
                    detalle_txt = "\n".join(extras)
                    if observaciones:
                        observaciones = f"{observaciones}\n{detalle_txt}"
                    else:
                        observaciones = detalle_txt

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
                    }
                )
                precio_unitario = menu_obj.precio_desayuno

            else:
                producto = None

            if producto is not None:
                consumos_inventario = []
                if tipo_form == 'general':
                    consumos_inventario = construir_consumos_receta_producto(producto)
                elif tipo_form == 'corriente':
                    consumos_inventario = construir_consumos_opciones_menu(
                        restaurante,
                        'corriente',
                        {
                            'sopa': corr_sopa,
                            'principio': corr_principio,
                            'proteina': corr_proteina,
                            'acompanante': corr_acompanante,
                        },
                    )
                elif tipo_form == 'desayuno':
                    consumos_inventario = construir_consumos_opciones_menu(
                        restaurante,
                        'desayuno',
                        {
                            'principal': des_principal,
                            'bebida': des_bebida,
                            'acompanante': des_acompanante,
                        },
                    )

                errores_stock = validar_stock_consumos(restaurante, consumos_inventario, cantidad)

                if not consumos_inventario and tipo_form == 'general':
                    ingredientes_qs = Ingrediente.objects.filter(nombre=producto.nombre)
                    if restaurante:
                        ingredientes_qs = ingredientes_qs.filter(restaurante=restaurante)

                    ingrediente = ingredientes_qs.first()
                    disponible = ingrediente.cantidad_actual if ingrediente else 0
                    if not ingrediente or disponible < cantidad:
                        errores_stock = [
                            f"No hay más stock disponible de {producto.nombre} para agregar al pedido."
                        ]

                if errores_stock:
                    messages.error(request, " ".join(errores_stock))
                else:
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        subtotal=precio_unitario * cantidad,
                        observaciones=observaciones,
                        consumos_inventario=consumos_inventario,
                    )

        return redirect('pedidos:detalle', orden_id=pedido.id)

    detalles = pedido.detalles.select_related('producto').all()
    productos_qs = Producto.objects.filter(disponible=True).exclude(
        nombre__in=PRODUCTOS_TECNICOS_MENU
    )
    if restaurante:
        productos_qs = productos_qs.filter(categoria__restaurante=restaurante)
    productos_qs = productos_qs.order_by('categoria__nombre', 'nombre')

    if categoria_id:
        productos_qs = productos_qs.filter(categoria_id=categoria_id)
    if query:
        productos_qs = productos_qs.filter(nombre__icontains=query)

    categorias = Categoria.objects.filter(activo=True)
    if restaurante:
        categorias = categorias.filter(restaurante=restaurante)

    # Asegurar que existan categorías base por restaurante
    categoria_corriente = categorias.filter(nombre__iexact='corriente').first()
    if not categoria_corriente:
        categoria_corriente = Categoria.objects.create(
            restaurante=restaurante,
            nombre='Corriente',
            activo=True,
        )

    categoria_desayuno = categorias.filter(nombre__iexact='desayuno').first()
    if not categoria_desayuno:
        categoria_desayuno = Categoria.objects.create(
            restaurante=restaurante,
            nombre='Desayuno',
            activo=True,
        )

    categoria_snacks = categorias.filter(nombre__iexact='snacks').first()
    if not categoria_snacks:
        categoria_snacks = Categoria.objects.create(
            restaurante=restaurante,
            nombre='Snacks',
            activo=True,
        )

    return render(request, 'pedidos/detalle.html', {
        'pedido': pedido,
        'detalles': detalles,
        'productos': productos_qs,
        'categorias': categorias,
        'categoria_id': categoria_id,
        'query': query,
        'categoria_corriente_id': categoria_corriente.id if categoria_corriente else None,
        'categoria_snacks': categoria_snacks,
        'show_corriente': show_corriente,
        'show_desayuno': show_desayuno,
        'menu_corriente': menu_corriente_data,
        'menu_desayuno': menu_desayuno_data,
    })


@login_required(login_url='login')
def detalle_pedido_productos_partial(request, orden_id):
    """Devuelve solo la sección HTML de productos del pedido para refresco parcial."""
    pedido = get_object_or_404(Pedido, pk=orden_id)
    _, rol_nombre, _ = get_empleado_rol_restaurante(request.user)
    if not caja_abierta(getattr(pedido, 'restaurante', None)):
        return JsonResponse({'detail': 'La caja está cerrada.'}, status=400)
    detalles = pedido.detalles.select_related('producto').all()

    contexto = {
        'pedido': pedido,
        'detalles': detalles,
        'rol_nombre': rol_nombre,
    }
    tbody_html = render_to_string('pedidos/_detalle_tbody.html', contexto, request=request)
    return JsonResponse(
        {
            'tbody': tbody_html,
            'total': float(pedido.total or 0),
        }
    )


@login_required(login_url='login')
def editar_pedido(request, orden_id):
    pedido = get_object_or_404(Pedido, pk=orden_id)
    if not caja_abierta(getattr(pedido, 'restaurante', None)):
        messages.warning(request, 'La caja está cerrada. No puedes editar pedidos.')
        return redirect('pedidos:lista')
    # No permitir editar pedidos que ya tienen factura (pagados)
    if hasattr(pedido, 'factura'):
        messages.error(request, 'No se puede editar este pedido porque ya fue pagado.')
        return redirect('pedidos:detalle', orden_id=pedido.id)

    restaurante = getattr(pedido, 'restaurante', None)

    # Menú corriente del día para ofrecer opciones en la edición
    _, menu_corriente_data, _ = menu_del_dia_data(restaurante)

    if request.method == 'POST':
        # Actualizar productos del pedido (detalles)
        detalles = list(pedido.detalles.select_related('producto').all())

        for detalle in detalles:
            eliminar_key = f'eliminar_{detalle.id}'
            cantidad_key = f'cantidad_{detalle.id}'
            producto_key = f'producto_{detalle.id}'
            sopa_key = f'corr_sopa_{detalle.id}'
            principio_key = f'corr_principio_{detalle.id}'
            proteina_key = f'corr_proteina_{detalle.id}'
            acompanante_key = f'corr_acompanante_{detalle.id}'

            # Si viene marcado para eliminar, lo borramos
            if eliminar_key in request.POST:
                detalle.delete()
                continue

            # Cambiar producto si se envió uno nuevo
            nuevo_producto_id = request.POST.get(producto_key)
            if nuevo_producto_id:
                try:
                    nuevo_producto_id_int = int(nuevo_producto_id)
                except (TypeError, ValueError):
                    nuevo_producto_id_int = None

                if nuevo_producto_id_int and nuevo_producto_id_int != detalle.producto_id:
                    nuevo_producto = get_object_or_404(Producto, pk=nuevo_producto_id_int, disponible=True)
                    detalle.producto = nuevo_producto
                    detalle.precio_unitario = nuevo_producto.precio

            # Actualizar cantidad si se envió
            nueva_cantidad = request.POST.get(cantidad_key)
            if nueva_cantidad is not None:
                try:
                    nueva_cantidad = int(nueva_cantidad)
                except (TypeError, ValueError):
                    nueva_cantidad = detalle.cantidad

                if nueva_cantidad <= 0:
                    # Cantidad 0 o negativa => eliminar
                    detalle.delete()
                    continue
                else:
                    detalle.cantidad = nueva_cantidad

            # Actualizar componentes de "corriente" (sopa, principio, proteína, acompañante)
            # Solo tiene sentido para los detalles que representan menú corriente
            base_lines = []
            current_sopa = current_principio = current_proteina = current_acompanante = None
            if detalle.observaciones:
                for linea in detalle.observaciones.splitlines():
                    txt = linea.strip()
                    lower = txt.lower()
                    if lower.startswith('sopa:'):
                        current_sopa = txt.split(':', 1)[1].strip()
                    elif lower.startswith('principio:'):
                        current_principio = txt.split(':', 1)[1].strip()
                    elif lower.startswith('proteina:'):
                        current_proteina = txt.split(':', 1)[1].strip()
                    elif lower.startswith('acompanante:'):
                        current_acompanante = txt.split(':', 1)[1].strip()
                    else:
                        base_lines.append(txt)

            # Nuevos valores enviados desde el formulario de edición
            new_sopa = request.POST.get(sopa_key, '').strip()
            new_principio = request.POST.get(principio_key, '').strip()
            new_proteina = request.POST.get(proteina_key, '').strip()
            new_acompanante = request.POST.get(acompanante_key, '').strip()

            final_sopa = new_sopa or current_sopa
            final_principio = new_principio or current_principio
            final_proteina = new_proteina or current_proteina
            final_acompanante = new_acompanante or current_acompanante

            extras = []
            if final_sopa:
                extras.append(f"Sopa: {final_sopa}")
            if final_principio:
                extras.append(f"Principio: {final_principio}")
            if final_proteina:
                extras.append(f"Proteina: {final_proteina}")
            if final_acompanante:
                extras.append(f"Acompanante: {final_acompanante}")

            if base_lines or extras:
                detalle.observaciones = "\n".join(base_lines + extras)
            else:
                detalle.observaciones = ''

            # Guardar cambios del detalle (cantidad, producto, observaciones)
            detalle.save()  # recalcula subtotal y total del pedido

        # Campos del propio pedido: estado y observaciones
        nuevo_estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones', '').strip()

        estados_validos = [e[0] for e in Pedido.ESTADOS]
        if nuevo_estado in estados_validos:
            pedido.estado = nuevo_estado
        pedido.observaciones = observaciones
        pedido.save(update_fields=['estado', 'observaciones'])

        # Asegurarnos de que el total esté coherente
        pedido.calcular_total()

        # Si el pedido ya no está activo (pagado, entregado o cancelado),
        # y no quedan más pedidos activos en la mesa, liberamos la mesa.
        if pedido.estado not in ESTADOS_PEDIDO_ACTIVOS:
            liberar_mesa_si_no_hay_pedidos_activos(pedido.mesa, excluir_pedido_id=pedido.id)

        return redirect('pedidos:detalle', orden_id=pedido.id)

    detalles = pedido.detalles.select_related('producto').all()
    productos = Producto.objects.filter(disponible=True).exclude(
        nombre__in=PRODUCTOS_TECNICOS_MENU
    ).order_by('categoria__nombre', 'nombre')

    return render(request, 'pedidos/pedidos_edit.html', {
        'pedido': pedido,
        'orden_id': pedido.id,
        'estados': Pedido.ESTADOS,
        'detalles': detalles,
        'productos': productos,
        'menu_corriente': menu_corriente_data,
    })

@login_required(login_url='login')
@require_POST
def eliminar_pedido(request, orden_id):
    """Elimina un pedido y, si no quedan más pedidos activos en la mesa, la libera."""
    pedido = get_object_or_404(Pedido, pk=orden_id)
    mesa = pedido.mesa

    # Guardamos el folio antes de eliminar para mostrar mensaje al usuario
    folio = pedido.id

    # Eliminamos el pedido
    pedido.delete()

    # Si la mesa no tiene más pedidos activos, la marcamos como libre
    liberar_mesa_si_no_hay_pedidos_activos(mesa)

    # Mostrar tarjeta de confirmación en el panel de pedidos
    messages.success(request, f"Se eliminó el pedido #{folio} correctamente.")
    return redirect('pedidos:lista')


@login_required(login_url='login')
@require_POST
def marcar_detalle_servido(request, detalle_id):
    """Marca un producto (detalle) como servido dentro de un pedido."""
    detalle = get_object_or_404(DetallePedido, pk=detalle_id)
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

    detalles_pedido = pedido.detalles.all()
    if detalles_pedido.exists() and all(d.servido for d in detalles_pedido):
        pedido.estado = 'entregado'
        pedido.save(update_fields=['estado'])
        liberar_mesa_si_no_hay_pedidos_activos(pedido.mesa, excluir_pedido_id=pedido.id)
    return redirect('pedidos:detalle', orden_id=pedido.id)
