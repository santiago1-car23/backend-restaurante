from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from decimal import Decimal

from apps.core.models import Restaurante
from apps.menu.models import Producto
from apps.mesas.models import Mesa


class Pedido(models.Model):
    def delete(self, *args, **kwargs):
        """Devuelve inventario de todos los detalles antes de eliminar el pedido."""
        for detalle in self.detalles.all():
            detalle.delete()
        super().delete(*args, **kwargs)
    """Pedidos de los clientes"""
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('en_preparacion', 'En preparación'),
        ('listo', 'Listo'),
        ('entregado', 'Servido'),
        ('cancelado', 'Cancelado'),
    )
    
    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='pedidos',
        help_text='Restaurante dueño de este pedido',
    )
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='pedidos')
    mesero = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pedidos_atendidos')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)
    archivado = models.BooleanField(default=False, help_text='Ocultar de la vista de pedidos activos cuando ya fue cerrado en caja')
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido #{self.id} - Mesa {self.mesa.numero}"
    
    def calcular_total(self):
        """Calcula el total del pedido sumando los detalles"""
        self.total = (
            DetallePedido.objects
            .filter(pedido=self)
            .aggregate(total=Sum('subtotal'))
            .get('total')
            or Decimal('0')
        )
        self.save()
        return self.total

class DetallePedido(models.Model):
    """Detalle de productos en cada pedido"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    observaciones = models.CharField(max_length=200, blank=True)
    servido = models.BooleanField(default=False)
    consumos_inventario = models.JSONField(default=list, blank=True)
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

    def _expandir_consumos(self, consumos, factor):
        resultado = []
        factor = Decimal(str(factor or 0))
        for consumo in consumos or []:
            cantidad = Decimal(str(consumo.get('cantidad') or 0)) * factor
            if cantidad <= 0:
                continue
            resultado.append(
                {
                    'ingrediente_id': consumo.get('ingrediente_id'),
                    'ingrediente_nombre': consumo.get('ingrediente_nombre'),
                    'cantidad': cantidad,
                    'unidad': consumo.get('unidad', 'unidad'),
                    'origen': consumo.get('origen', 'detalle'),
                    'opcion': consumo.get('opcion', ''),
                }
            )
        return resultado

    def _consumos_totales_actuales(self):
        if self.consumos_inventario:
            return self._expandir_consumos(self.consumos_inventario, self.cantidad)
        return []

    def _ajustar_consumos(self, consumos, signo):
        from apps.inventario.models import Ingrediente, MovimientoInventario

        for consumo in consumos or []:
            ingrediente_id = consumo.get('ingrediente_id')
            if not ingrediente_id:
                continue

            ingrediente = Ingrediente.objects.filter(id=ingrediente_id).first()
            if not ingrediente:
                continue

            cantidad = Decimal(str(consumo.get('cantidad') or 0))
            if cantidad <= 0:
                continue

            if signo > 0:
                ingrediente.cantidad_actual -= cantidad
                tipo = 'salida'
                motivo = (
                    f"Pedido mesa #{self.pedido.mesa.numero if self.pedido.mesa else ''} - "
                    f"{self.producto.nombre} / {consumo.get('ingrediente_nombre', ingrediente.nombre)}"
                )
            else:
                ingrediente.cantidad_actual += cantidad
                tipo = 'entrada'
                motivo = (
                    f"Devolución/ajuste pedido mesa #{self.pedido.mesa.numero if self.pedido.mesa else ''} - "
                    f"{self.producto.nombre} / {consumo.get('ingrediente_nombre', ingrediente.nombre)}"
                )

            ingrediente.save(update_fields=["cantidad_actual"])
            MovimientoInventario.objects.create(
                ingrediente=ingrediente,
                tipo=tipo,
                cantidad=cantidad,
                motivo=motivo,
                usuario=None,
            )

    def _ajustar_inventario(self, producto, delta):
        """Ajusta inventario y registra movimiento.

        `delta` positivo descuenta stock.
        `delta` negativo devuelve stock.
        """
        from apps.inventario.models import Ingrediente, MovimientoInventario

        if not producto or not delta:
            return

        ingrediente = Ingrediente.objects.filter(
            nombre=producto.nombre,
            restaurante=self.pedido.restaurante,
        ).first()
        if not ingrediente:
            return

        cantidad = abs(delta)
        if delta > 0:
            ingrediente.cantidad_actual -= cantidad
            tipo = 'salida'
            motivo = (
                f"Pedido mesa #{self.pedido.mesa.numero if self.pedido.mesa else ''} - "
                f"{producto.nombre}"
            )
        else:
            ingrediente.cantidad_actual += cantidad
            tipo = 'entrada'
            motivo = (
                f"Devolución/ajuste pedido mesa #{self.pedido.mesa.numero if self.pedido.mesa else ''} - "
                f"{producto.nombre}"
            )

        ingrediente.save(update_fields=["cantidad_actual"])
        MovimientoInventario.objects.create(
            ingrediente=ingrediente,
            tipo=tipo,
            cantidad=cantidad,
            motivo=motivo,
            usuario=None,
        )
    
    def save(self, *args, **kwargs):
        """Calcula subtotal y sincroniza inventario incluso en ediciones."""
        is_new = self.pk is None
        old_producto = None
        old_cantidad = 0

        if not is_new:
            old = type(self).objects.get(pk=self.pk)
            old_producto = old.producto
            old_cantidad = old.cantidad

        self.subtotal = self.cantidad * self.precio_unitario

        super().save(*args, **kwargs)

        consumos_actuales = self._consumos_totales_actuales()

        if is_new:
            if consumos_actuales:
                self._ajustar_consumos(consumos_actuales, 1)
            else:
                self._ajustar_inventario(self.producto, self.cantidad)
        else:
            old_consumos = old.consumos_inventario if old else []
            old_consumos_totales = self._expandir_consumos(old_consumos, old_cantidad)
            cambio_producto = old_producto is not None and old_producto.id != self.producto_id
            cambio_consumos = old_consumos != self.consumos_inventario

            if old_consumos_totales or consumos_actuales:
                if old_consumos_totales:
                    self._ajustar_consumos(old_consumos_totales, -1)
                if consumos_actuales:
                    self._ajustar_consumos(consumos_actuales, 1)
            elif cambio_producto:
                self._ajustar_inventario(old_producto, -old_cantidad)
                self._ajustar_inventario(self.producto, self.cantidad)
            else:
                delta = self.cantidad - old_cantidad
                self._ajustar_inventario(self.producto, delta)

        # Actualiza el total del pedido
        self.pedido.calcular_total()

    def delete(self, *args, **kwargs):
        """Devuelve inventario al eliminar el detalle."""
        consumos_actuales = self._consumos_totales_actuales()
        if consumos_actuales:
            self._ajustar_consumos(consumos_actuales, -1)
        else:
            self._ajustar_inventario(self.producto, -self.cantidad)
        super().delete(*args, **kwargs)
