from django.db import models
from django.contrib.auth.models import User

from apps.core.models import Restaurante
from apps.menu.models import Producto
from apps.mesas.models import Mesa


class Pedido(models.Model):
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
        self.total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.save()
        return self.total

class DetallePedido(models.Model):
    """Detalle de productos en cada pedido"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.CharField(max_length=200, blank=True)
    servido = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
    
    def save(self, *args, **kwargs):
        """Calcula el subtotal antes de guardar"""
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        # Actualiza el total del pedido
        self.pedido.calcular_total()
