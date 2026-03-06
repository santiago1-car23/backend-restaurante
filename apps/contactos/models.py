from django.db import models

from apps.core.models import Restaurante


class Proveedor(models.Model):
    """Proveedores del restaurante"""
    TIPOS = (
        ('alimentos', 'Alimentos'),
        ('bebidas', 'Bebidas'),
        ('limpieza', 'Limpieza'),
        ('tecnologia', 'Tecnología'),
        ('otros', 'Otros'),
    )

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='proveedores',
        help_text='Restaurante dueño de este proveedor',
    )
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=30, blank=True)
    telefono_secundario = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='otros')
    notas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class TelefonoNegocio(models.Model):
    """Números importantes del negocio (domicilios, reservas, etc.)"""

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='telefonos_negocio',
        help_text='Restaurante dueño de este número',
    )
    nombre = models.CharField(max_length=100, help_text='Ej: Teléfono principal, Domicilios, WhatsApp')
    numero = models.CharField(max_length=30)
    notas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Teléfono del negocio'
        verbose_name_plural = 'Teléfonos del negocio'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.numero}"
