from django.db import models

from apps.core.models import Restaurante
from apps.menu.models import Producto


class Ingrediente(models.Model):
    """Ingredientes para el inventario"""
    UNIDADES = (
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('unidad', 'Unidades'),
    )
    
    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ingredientes',
        help_text='Restaurante dueño de este ingrediente',
    )
    nombre = models.CharField(max_length=200)
    unidad = models.CharField(max_length=10, choices=UNIDADES)
    cantidad_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_minima = models.DecimalField(max_digits=10, decimal_places=2, help_text='Alerta cuando esté por debajo')
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.cantidad_actual} {self.unidad})"
    
    def alerta_stock(self):
        """Retorna True si está por debajo del mínimo"""
        return self.cantidad_actual <= self.cantidad_minima

class MovimientoInventario(models.Model):
    """Registro de movimientos de inventario"""
    TIPOS = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    )
    
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=200)
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.tipo} - {self.ingrediente.nombre} ({self.cantidad})"
    
    def save(self, *args, **kwargs):
        """Actualiza el stock del ingrediente"""
        super().save(*args, **kwargs)
        if self.tipo == 'entrada':
            self.ingrediente.cantidad_actual += self.cantidad
        elif self.tipo == 'salida':
            self.ingrediente.cantidad_actual -= self.cantidad
        elif self.tipo == 'ajuste':
            self.ingrediente.cantidad_actual = self.cantidad
        self.ingrediente.save()
