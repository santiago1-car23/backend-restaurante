from django.db import models
from django.contrib.auth.models import User
from apps.core.models import Restaurante


class Rol(models.Model):
    """Roles del sistema: admin, mesero, cajero, cocinero"""
    ROLES = (
        ('admin', 'Administrador'),
        ('mesero', 'Mesero'),
        ('cajero', 'Cajero'),
        ('cocinero', 'Cocinero'),
    )

    nombre = models.CharField(max_length=20, choices=ROLES, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.get_nombre_display()

class Empleado(models.Model):
    """Extiende el modelo User con datos del empleado"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empleado')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, related_name='empleados')
    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='empleados',
        help_text='Restaurante al que pertenece este empleado',
    )
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    hora_entrada = models.TimeField(null=True, blank=True, help_text='Hora habitual de inicio de turno')
    hora_salida = models.TimeField(null=True, blank=True, help_text='Hora habitual de fin de turno')
    fecha_contratacion = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rol}"

    def save(self, *args, **kwargs):
        # Si el rol es administrador, dar permisos de staff y superusuario
        if self.rol and self.rol.nombre == 'admin':
            self.user.is_staff = True
            self.user.is_superuser = True
            self.user.save()
        # Si se cambia de rol y ya no es admin, se podrían quitar permisos,
        # pero por seguridad a veces es mejor no hacerlo automáticamente 
        # o hacerlo con cuidado. Por ahora solo garantizamos que el admin tenga permisos.
        
        super().save(*args, **kwargs)


class Notificacion(models.Model):
    """Notificaciones simples para usuarios (por ejemplo, pedidos listos para servir)."""

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notificaciones',
    )
    mensaje = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    creada = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-creada']

    def __str__(self):
        return f"Notificación para {self.usuario}: {self.mensaje[:40]}"
