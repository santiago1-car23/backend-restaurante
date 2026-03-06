from django.core.management.base import BaseCommand
from apps.mesas.models import Mesa


class Command(BaseCommand):
    help = 'Crea mesas de ejemplo para el restaurante'

    def handle(self, *args, **kwargs):
        mesas_data = [
            {'numero': 1, 'capacidad': 2, 'ubicacion': 'Terraza'},
            {'numero': 2, 'capacidad': 4, 'ubicacion': 'Interior'},
            {'numero': 3, 'capacidad': 4, 'ubicacion': 'Interior'},
            {'numero': 4, 'capacidad': 6, 'ubicacion': 'Interior'},
            {'numero': 5, 'capacidad': 2, 'ubicacion': 'Terraza'},
            {'numero': 6, 'capacidad': 4, 'ubicacion': 'VIP'},
            {'numero': 7, 'capacidad': 8, 'ubicacion': 'VIP'},
            {'numero': 8, 'capacidad': 2, 'ubicacion': 'Barra'},
        ]

        for m_data in mesas_data:
            mesa, created = Mesa.objects.get_or_create(
                numero=m_data['numero'],
                defaults={
                    'capacidad': m_data['capacidad'],
                    'ubicacion': m_data['ubicacion'],
                    'estado': 'libre',
                    'activa': True,
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Mesa #{mesa.numero} - Cap: {mesa.capacidad} - {mesa.ubicacion}'
                    )
                )

        self.stdout.write(self.style.SUCCESS(f'\n✅ {Mesa.objects.count()} mesas creadas/verificadas'))
