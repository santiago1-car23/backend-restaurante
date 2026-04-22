from apps.mesas.models import Mesa
from apps.pedidos.models import Pedido


def archivar_pedidos_y_liberar_mesas(restaurante):
    """Cierra visualmente la operación del día al archivar pedidos y liberar mesas."""
    pedidos_qs = Pedido.objects.filter(archivado=False)
    if restaurante is not None:
        pedidos_qs = pedidos_qs.filter(restaurante=restaurante)

    mesa_ids = list(
        pedidos_qs.exclude(mesa__numero=0).values_list('mesa_id', flat=True).distinct()
    )

    pedidos_qs.update(archivado=True)

    if mesa_ids:
        Mesa.objects.filter(id__in=mesa_ids).update(estado='libre')
