from django.core.management.base import BaseCommand
from apps.menu.models import Categoria, Producto


class Command(BaseCommand):
    help = 'Carga categorías y productos de ejemplo'

    def handle(self, *args, **kwargs):
        # Crear categorías
        bebidas, created = Categoria.objects.get_or_create(
            nombre='Bebidas',
            defaults={'descripcion': 'Bebidas frías y calientes'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Categoría creada: {bebidas.nombre}'))
        
        platos, created = Categoria.objects.get_or_create(
            nombre='Platos',
            defaults={'descripcion': 'Platos principales'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Categoría creada: {platos.nombre}'))
        
        postres, created = Categoria.objects.get_or_create(
            nombre='Postres',
            defaults={'descripcion': 'Postres y dulces'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Categoría creada: {postres.nombre}'))

        # Crear productos
        productos_data = [
            # Bebidas
            {'nombre': 'Coca-Cola', 'precio': 3000, 'categoria': bebidas},
            {'nombre': 'Agua', 'precio': 2000, 'categoria': bebidas},
            {'nombre': 'Jugo Natural', 'precio': 4500, 'categoria': bebidas},
            {'nombre': 'Café', 'precio': 2500, 'categoria': bebidas},
            
            # Platos
            {'nombre': 'Bandeja Paisa', 'precio': 18000, 'categoria': platos},
            {'nombre': 'Pollo Asado', 'precio': 15000, 'categoria': platos},
            {'nombre': 'Pescado Frito', 'precio': 20000, 'categoria': platos},
            {'nombre': 'Hamburguesa', 'precio': 12000, 'categoria': platos},
            
            # Postres
            {'nombre': 'Helado', 'precio': 5000, 'categoria': postres},
            {'nombre': 'Flan', 'precio': 4000, 'categoria': postres},
            {'nombre': 'Tres Leches', 'precio': 6000, 'categoria': postres},
        ]

        for p_data in productos_data:
            producto, created = Producto.objects.get_or_create(
                nombre=p_data['nombre'],
                defaults={
                    'precio': p_data['precio'],
                    'categoria': p_data['categoria'],
                    'disponible': True,
                    'tiempo_preparacion': 15,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Producto: {producto.nombre} - ${producto.precio}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Categorías y productos cargados exitosamente'))
