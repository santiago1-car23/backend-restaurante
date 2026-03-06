"""
Comando para crear mesas de prueba si no existen.
"""

from django.core.management.base import BaseCommand
from apps.core.models import Restaurante
from apps.mesas.models import Mesa


class Command(BaseCommand):
    help = 'Crea mesas de prueba para el restaurante'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=20,
            help='Número de mesas a crear (default: 20)',
        )

    def handle(self, *args, **options):
        restaurante = Restaurante.objects.first()
        if not restaurante:
            self.stdout.write(
                self.style.ERROR('❌ No hay restaurante. Crea uno en admin primero.')
            )
            return

        cantidad = options['cantidad']
        mesas_existentes = Mesa.objects.filter(restaurante=restaurante).count()
        
        if mesas_existentes > 0:
            self.stdout.write(
                self.style.WARNING(f'ℹ️  Ya existen {mesas_existentes} mesas. Creando {cantidad} más...')
            )
            numero_inicio = Mesa.objects.filter(restaurante=restaurante).aggregate(max=models.Max('numero'))['max'] or 0
            numero_inicio += 1
        else:
            numero_inicio = 1

        for i in range(cantidad):
            Mesa.objects.get_or_create(
                restaurante=restaurante,
                numero=numero_inicio + i,
                defaults={
                    'capacidad': 4,
                    'ubicacion': 'Interna' if i % 2 == 0 else 'Terraza',
                }
            )

        total = Mesa.objects.filter(restaurante=restaurante).count()
        self.stdout.write(
            self.style.SUCCESS(f'✅ {total} mesas disponibles para {restaurante.nombre}')
        )
