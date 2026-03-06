from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from apps.caja.models import CajaSesion

class Command(BaseCommand):
    help = 'Corrige campos de fecha en CajaSesion que sean string en vez de datetime.'

    def handle(self, *args, **options):
        corregidos = 0
        for sesion in CajaSesion.objects.all():
            # Verifica y corrige fecha_apertura
            if isinstance(sesion.fecha_apertura, str):
                dt = parse_datetime(sesion.fecha_apertura)
                if dt:
                    sesion.fecha_apertura = dt
                    corregidos += 1
            # Verifica y corrige fecha_cierre
            if sesion.fecha_cierre and isinstance(sesion.fecha_cierre, str):
                dt = parse_datetime(sesion.fecha_cierre)
                if dt:
                    sesion.fecha_cierre = dt
                    corregidos += 1
            sesion.save()
        self.stdout.write(self.style.SUCCESS(f'Campos corregidos: {corregidos}'))
