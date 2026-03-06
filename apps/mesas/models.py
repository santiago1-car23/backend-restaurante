from django.db import models

from apps.core.models import Restaurante


class Mesa(models.Model):
    """Mesas del restaurante"""
    ESTADOS = (
        ('libre', 'Libre'),
        ('ocupada', 'Ocupada'),
        ('reservada', 'Reservada'),
    )
    
    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='mesas',
        help_text='Restaurante dueño de esta mesa',
    )
    numero = models.IntegerField()
    capacidad = models.IntegerField(default=4)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='libre')
    ubicacion = models.CharField(max_length=100, blank=True, help_text='Ej: Terraza, Interior, VIP')
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'
        ordering = ['numero']
        unique_together = ('restaurante', 'numero')
    
    def __str__(self):
        return f"Mesa {self.numero} - {self.get_estado_display()}"
