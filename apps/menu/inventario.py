from decimal import Decimal

from apps.inventario.models import Ingrediente
from apps.menu.models import ConsumoOpcionMenu, RecetaProducto


def _decimal(value):
    return value if isinstance(value, Decimal) else Decimal(str(value or 0))


def _normalizar_nombre(valor: str) -> str:
    return (valor or '').strip().lower()


def construir_consumos_receta_producto(producto):
    """Devuelve consumos por unidad para un producto, si tiene receta."""
    try:
        receta = producto.receta
    except RecetaProducto.DoesNotExist:
        return []

    if not receta.activo:
        return []

    consumos = []
    for item in receta.ingredientes.select_related('ingrediente').all():
        consumos.append(
            {
                'ingrediente_id': item.ingrediente_id,
                'ingrediente_nombre': item.ingrediente.nombre,
                'cantidad': str(item.cantidad),
                'unidad': item.ingrediente.unidad,
                'origen': 'receta_producto',
            }
        )
    return consumos


def construir_consumos_opciones_menu(restaurante, tipo_menu, opciones):
    """Devuelve consumos por unidad según las opciones elegidas en corriente/desayuno."""
    if not restaurante:
        return []

    consumos = []
    for categoria_opcion, nombre_opcion in (opciones or {}).items():
        nombre_opcion = (nombre_opcion or '').strip()
        if not nombre_opcion:
            continue

        qs = ConsumoOpcionMenu.objects.select_related('ingrediente').filter(
            restaurante=restaurante,
            tipo_menu=tipo_menu,
            categoria_opcion=categoria_opcion,
            activo=True,
        )

        items = [item for item in qs if _normalizar_nombre(item.nombre_opcion) == _normalizar_nombre(nombre_opcion)]
        for item in items:
            consumos.append(
                {
                    'ingrediente_id': item.ingrediente_id,
                    'ingrediente_nombre': item.ingrediente.nombre,
                    'cantidad': str(item.cantidad),
                    'unidad': item.ingrediente.unidad,
                    'origen': f'{tipo_menu}:{categoria_opcion}',
                    'opcion': nombre_opcion,
                }
            )

    return consumos


def validar_stock_consumos(restaurante, consumos_por_unidad, cantidad_detalle):
    """Valida stock disponible para una lista de consumos por unidad."""
    errores = []
    cantidad_detalle = _decimal(cantidad_detalle)

    for consumo in consumos_por_unidad or []:
        ingrediente_id = consumo.get('ingrediente_id')
        cantidad_total = _decimal(consumo.get('cantidad')) * cantidad_detalle
        if not ingrediente_id or cantidad_total <= 0:
            continue

        ingrediente = Ingrediente.objects.filter(id=ingrediente_id).first()
        if restaurante and ingrediente and ingrediente.restaurante_id != restaurante.id:
            ingrediente = None

        if not ingrediente:
            errores.append(f"No se encontró el ingrediente configurado para {consumo.get('ingrediente_nombre', 'la receta')}.")
            continue

        if ingrediente.cantidad_actual < cantidad_total:
            errores.append(
                f"Stock insuficiente de {ingrediente.nombre}. "
                f"Necesitas {cantidad_total} {ingrediente.unidad} y tienes {ingrediente.cantidad_actual}."
            )

    return errores
