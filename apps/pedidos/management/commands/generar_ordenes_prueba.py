"""
Comando para generar 500 órdenes de prueba para probar scroll y comportamiento del sistema.

Uso: python manage.py generar_ordenes_prueba [--count=500]
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

from apps.core.models import Restaurante
from apps.mesas.models import Mesa
from apps.menu.models import Producto
from apps.pedidos.models import Pedido, DetallePedido


class Command(BaseCommand):
    help = 'Genera órdenes de prueba para test de scroll y rendimiento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=500,
            help='Número de órdenes a generar (default: 500)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Validar datos necesarios
        restaurante = Restaurante.objects.first()
        if not restaurante:
            raise CommandError('No hay restaurantes en la BD. Crea uno primero.')
        
        mesas = Mesa.objects.filter(restaurante=restaurante)
        if not mesas.exists():
            raise CommandError(f'No hay mesas para {restaurante.nombre}. Crea mesas primero.')
        
        usuarios = User.objects.filter(is_staff=False)
        if not usuarios.exists():
            usuarios = [User.objects.first()]
        
        productos = Producto.objects.filter(disponible=True)
        if not productos.exists():
            raise CommandError('No hay productos disponibles. Crea productos primero.')

        self.stdout.write(
            self.style.SUCCESS(f'🚀 Iniciando generación de {count} órdenes...')
        )
        self.stdout.write(f'   Restaurante: {restaurante.nombre}')
        self.stdout.write(f'   Mesas: {mesas.count()}')
        self.stdout.write(f'   Productos: {productos.count()}')
        self.stdout.write(f'   Usuarios: {usuarios.count()}')

        estados = [estado[0] for estado in Pedido.ESTADOS]
        generadas = 0
        
        try:
            for i in range(count):
                # Datos aleatorios
                mesa = random.choice(mesas)
                mesero = random.choice(usuarios)
                estado = random.choice(estados)
                
                # Crear pedido con fecha variable para simular histórico
                dias_atras = random.randint(0, 30)
                fecha = timezone.now() - timedelta(days=dias_atras)
                
                pedido = Pedido.objects.create(
                    restaurante=restaurante,
                    mesa=mesa,
                    mesero=mesero,
                    estado=estado,
                    fecha_creacion=fecha,
                    fecha_actualizacion=fecha,
                    observaciones=f'Orden de prueba #{i+1}' if random.random() > 0.7 else '',
                    archivado=random.choice([True, False]) if estado in ['entregado', 'cancelado'] else False,
                )
                
                # Agregar 1-4 detalles por pedido
                num_detalles = random.randint(1, 4)
                for _ in range(num_detalles):
                    producto = random.choice(productos)
                    cantidad = random.randint(1, 3)
                    
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio,
                        observaciones='Extra picante' if random.random() > 0.8 else '',
                        servido=estado == 'entregado',
                    )
                
                # Recalcular total
                pedido.calcular_total()
                
                generadas += 1
                
                # Progress feedback cada 50
                if generadas % 50 == 0:
                    self.stdout.write(
                        self.style.WARNING(f'   ⏳ {generadas}/{count}...')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ {generadas} órdenes generadas exitosamente!')
            )
            self.stdout.write(
                self.style.SUCCESS(f'   📊 Total en BD: {Pedido.objects.count()} pedidos')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Error al generar órdenes: {str(e)}')
            )
            raise
