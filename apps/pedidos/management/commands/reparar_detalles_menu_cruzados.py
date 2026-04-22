from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.menu.models import Categoria, MenuDiario, Producto
from apps.pedidos.models import DetallePedido


class Command(BaseCommand):
    help = (
        "Repara detalles de pedidos que quedaron guardados como productos normales "
        "pero con observaciones de menu corriente."
    )

    def handle(self, *args, **options):
        sospechosos = DetallePedido.objects.select_related(
            'pedido__restaurante',
            'producto__categoria',
        ).filter(
            Q(observaciones__icontains='Sopa:')
            & Q(observaciones__icontains='Principio:')
            & Q(observaciones__icontains='Proteina:')
            & Q(observaciones__icontains='Acompanante:')
        ).exclude(
            producto__nombre='Menu corriente',
        )

        reparados = 0
        omitidos = 0

        for detalle in sospechosos:
            pedido = detalle.pedido
            restaurante = getattr(pedido, 'restaurante', None)
            fecha_menu = pedido.fecha_creacion.date() if pedido.fecha_creacion else None
            menu_obj = None
            if restaurante and fecha_menu:
                menu_obj = MenuDiario.objects.filter(
                    restaurante=restaurante,
                    fecha=fecha_menu,
                ).first()
            if not menu_obj and restaurante and fecha_menu:
                menu_obj = (
                    MenuDiario.objects.filter(
                        restaurante=restaurante,
                        fecha__lte=fecha_menu,
                    )
                    .order_by('-fecha')
                    .first()
                )
            if not menu_obj and restaurante:
                menu_obj = (
                    MenuDiario.objects.filter(restaurante=restaurante)
                    .order_by('-fecha')
                    .first()
                )

            if not menu_obj:
                omitidos += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Omitido detalle #{detalle.id}: no existe menu del dia para {fecha_menu}."
                    )
                )
                continue

            categoria_corriente, _ = Categoria.objects.get_or_create(
                restaurante=restaurante,
                nombre='Corriente',
                defaults={'activo': True},
            )
            if not categoria_corriente.activo:
                categoria_corriente.activo = True
                categoria_corriente.save(update_fields=['activo'])

            producto_corriente, _ = Producto.objects.get_or_create(
                nombre='Menu corriente',
                categoria=categoria_corriente,
                defaults={
                    'descripcion': 'Menu del dia',
                    'precio': menu_obj.precio_completo,
                    'disponible': True,
                    'tiempo_preparacion': 15,
                },
            )

            lineas = [linea.strip() for linea in (detalle.observaciones or '').splitlines() if linea.strip()]
            sopa_line = next((linea for linea in lineas if linea.lower().startswith('sopa:')), '')
            sopa_valor = sopa_line.split(':', 1)[1].strip().lower() if ':' in sopa_line else ''
            tiene_sopa = sopa_valor and sopa_valor not in ['sin sopa']

            principio = any(linea.lower().startswith('principio:') and linea.split(':', 1)[1].strip() for linea in lineas if ':' in linea)
            proteina = any(linea.lower().startswith('proteina:') and linea.split(':', 1)[1].strip() for linea in lineas if ':' in linea)
            acompanante = any(linea.lower().startswith('acompanante:') and linea.split(':', 1)[1].strip() for linea in lineas if ':' in linea)
            tiene_otros = principio or proteina or acompanante

            if tiene_sopa and not tiene_otros and menu_obj.precio_sopa is not None:
                precio_unitario = menu_obj.precio_sopa
            elif tiene_sopa:
                precio_unitario = menu_obj.precio_completo
            else:
                precio_unitario = menu_obj.precio_bandeja

            detalle.producto = producto_corriente
            detalle.precio_unitario = precio_unitario
            detalle.save()

            reparados += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Reparado detalle #{detalle.id}: ahora es Menu corriente por {precio_unitario}."
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Proceso terminado. Reparados: {reparados}. Omitidos: {omitidos}."
            )
        )
