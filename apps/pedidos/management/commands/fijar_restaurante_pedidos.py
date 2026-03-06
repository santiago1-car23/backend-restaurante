from django.core.management.base import BaseCommand

from apps.pedidos.models import Pedido


class Command(BaseCommand):
    help = "Asigna el restaurante a pedidos antiguos usando la mesa asociada cuando el campo restaurante está vacío."

    def handle(self, *args, **options):
        encontrados = Pedido.objects.filter(restaurante__isnull=True, mesa__isnull=False)
        total = encontrados.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No hay pedidos pendientes por actualizar."))
            return

        actualizados = 0
        for pedido in encontrados.select_related('mesa__restaurante'):
            restaurante = getattr(getattr(pedido, 'mesa', None), 'restaurante', None)
            if restaurante is None:
                continue
            pedido.restaurante = restaurante
            pedido.save(update_fields=['restaurante'])
            actualizados += 1

        self.stdout.write(self.style.SUCCESS(f"Pedidos actualizados: {actualizados} de {total}"))
