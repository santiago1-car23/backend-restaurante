from datetime import date

from apps.caja.models import CajaSesion
from apps.menu.models import MenuDiario
from apps.usuarios.models import Notificacion


ESTADOS_PEDIDO_ACTIVOS = ['pendiente', 'en_preparacion', 'listo']


def get_empleado_rol_restaurante(user):
    """Obtiene empleado, rol y restaurante del usuario de forma segura."""
    empleado = getattr(user, 'empleado', None)
    rol_nombre = ''
    restaurante = None

    if empleado is not None:
        rol = getattr(empleado, 'rol', None)
        if rol is not None:
            rol_nombre = getattr(rol, 'nombre', '') or ''
        restaurante = getattr(empleado, 'restaurante', None)

    return empleado, rol_nombre, restaurante


def rol_usuario(user):
    return get_empleado_rol_restaurante(user)[1]


def restaurante_usuario(user):
    return get_empleado_rol_restaurante(user)[2]


def caja_abierta(restaurante):
    if restaurante is None:
        return CajaSesion.obtener_activa() is not None
    return CajaSesion.obtener_activa(restaurante=restaurante) is not None


def puede_escribir_pedidos(user):
    return user and user.is_authenticated and rol_usuario(user) in ['admin', 'mesero', 'cajero']


def puede_marcar_servido(user):
    return user and user.is_authenticated and rol_usuario(user) in ['admin', 'mesero', 'cajero', 'cocinero']


def split_lista(valor):
    return [v.strip() for v in valor.split(',') if v.strip()] if valor else []


def menu_del_dia_data(restaurante, fecha_sel=None):
    if not restaurante:
        return None, None, None

    fecha_sel = fecha_sel or date.today()
    menu_obj = MenuDiario.objects.filter(fecha=fecha_sel, restaurante=restaurante).first()
    if not menu_obj:
        return None, None, fecha_sel

    menu_corriente_data = {
        'sopa': menu_obj.sopa,
        'sopas': split_lista(menu_obj.sopa),
        'principio': split_lista(menu_obj.principios),
        'proteina': split_lista(menu_obj.proteinas),
        'acompanante': menu_obj.acompanante,
        'limonada': menu_obj.limonada,
        'precio_sopa': menu_obj.precio_sopa,
        'precio_bandeja': menu_obj.precio_bandeja,
        'precio_completo': menu_obj.precio_completo,
    }

    menu_desayuno_data = None
    if menu_obj.desayuno_principales or menu_obj.desayuno_bebidas or menu_obj.precio_desayuno:
        menu_desayuno_data = {
            'principales': split_lista(menu_obj.desayuno_principales),
            'bebidas': split_lista(menu_obj.desayuno_bebidas),
            'acompanante': menu_obj.desayuno_acompanante,
            'precio_desayuno': menu_obj.precio_desayuno,
            'caldos': split_lista(menu_obj.caldos),
        }

    return menu_obj, menu_corriente_data, menu_desayuno_data


def liberar_mesa_si_no_hay_pedidos_activos(mesa, excluir_pedido_id=None):
    if mesa is None:
        return

    pedidos_activos = mesa.pedidos.filter(
        archivado=False,
        estado__in=ESTADOS_PEDIDO_ACTIVOS,
    )
    if excluir_pedido_id is not None:
        pedidos_activos = pedidos_activos.exclude(id=excluir_pedido_id)

    if not pedidos_activos.exists() and mesa.estado != 'libre':
        mesa.estado = 'libre'
        mesa.save(update_fields=['estado'])


def notificar_mesero_pedido_listo(pedido):
    """Crea una notificación para el mesero cuando el pedido queda listo para servir."""
    mesero = getattr(pedido, 'mesero', None)
    mesa = getattr(pedido, 'mesa', None)
    if mesero is None:
        return

    mesa_label = f"Mesa {mesa.numero}" if mesa is not None else "mesa sin asignar"
    mensaje = f"Pedido #{pedido.id} de {mesa_label} listo para servir."
    url = f"/detalle?id={pedido.id}"

    # Evita duplicados recientes por doble clic o reintentos.
    if Notificacion.objects.filter(usuario=mesero, mensaje=mensaje, leida=False).exists():
        return

    Notificacion.objects.create(
        usuario=mesero,
        mensaje=mensaje,
        url=url,
    )
