from django.core.management.base import BaseCommand

from apps.pedidos.models import Pedido
from apps.caja.models import CajaSesion, Factura, MovimientoCaja
from apps.inventario.models import MovimientoInventario


class Command(BaseCommand):
    help = "Limpia historiales antiguos: pedidos archivados, facturas, sesiones de caja cerradas y movimientos de inventario."

    def handle(self, *args, **options):
        # Borrar movimientos de inventario (solo historial, no ingredientes)
        mov_inv_count, _ = MovimientoInventario.objects.all().delete()

        # Borrar facturas (historial de ventas)
        facturas_count, _ = Factura.objects.all().delete()

        # Borrar sesiones de caja cerradas y sus movimientos
        cajas_qs = CajaSesion.objects.filter(estado="cerrada")
        cajas_count = cajas_qs.count()
        mov_caja_count, _ = MovimientoCaja.objects.filter(sesion__in=cajas_qs).delete()
        cajas_qs.delete()

        # Borrar pedidos archivados (historial de pedidos ya cerrados)
        pedidos_qs = Pedido.objects.filter(archivado=True)
        pedidos_count, _ = pedidos_qs.delete()

        self.stdout.write(self.style.SUCCESS("Historial limpiado:"))
        self.stdout.write(f"  Movimientos de inventario eliminados: {mov_inv_count}")
        self.stdout.write(f"  Facturas eliminadas: {facturas_count}")
        self.stdout.write(f"  Movimientos de caja eliminados: {mov_caja_count}")
        self.stdout.write(f"  Sesiones de caja cerradas eliminadas: {cajas_count}")
        self.stdout.write(f"  Pedidos archivados eliminados: {pedidos_count}")
