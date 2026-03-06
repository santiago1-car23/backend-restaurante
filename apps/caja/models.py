from django.db import models
from django.contrib.auth.models import User

from apps.core.models import Restaurante
from apps.pedidos.models import Pedido


class CajaSesion(models.Model):
    """Sesiones de caja (apertura / cierre)"""

    ESTADOS = (
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
    )

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sesiones_caja',
        help_text='Restaurante al que pertenece esta sesión de caja',
    )

    usuario_apertura = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cajas_abiertas',
    )
    usuario_cierre = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cajas_cerradas',
    )
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='abierta')

    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Dinero que entra a la caja por fuera de las facturas (ventas sueltas, recargas, etc.)
    entradas_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Dinero que sale de la caja (pagos a proveedores, retiros, etc.)
    salidas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Sesión de caja'
        verbose_name_plural = 'Sesiones de caja'
        ordering = ['-fecha_apertura']

    def __str__(self):
        return f"Caja {self.id} - {self.get_estado_display()} - {self.fecha_apertura:%d/%m/%Y %H:%M}"

    @classmethod
    def obtener_activa(cls, restaurante=None):
        """Devuelve la sesión de caja abierta para un restaurante (si existe).

        Si restaurante es None, devuelve la primera sesión abierta global.
        """
        qs = cls.objects.filter(estado='abierta')
        if restaurante is not None:
            qs = qs.filter(restaurante=restaurante)
        return qs.order_by('-fecha_apertura').first()

    @property
    def total_facturado(self):
        from django.db.models import Sum
        return self.facturas.aggregate(total=Sum('total'))['total'] or 0

    @property
    def resultado_neto(self):
        """Resultado del día para la sesión.

        Total facturado + entradas extra - salidas.
        """
        return (
            (self.total_facturado or 0)
            + (self.entradas_extra or 0)
            - (self.salidas or 0)
        )


class Factura(models.Model):
    """Facturas de los pedidos"""
    METODOS_PAGO = (
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('mixto', 'Mixto'),
    )

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='factura')
    sesion = models.ForeignKey(
        CajaSesion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='facturas',
    )
    numero_factura = models.CharField(max_length=20, unique=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    cajero = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='facturas_emitidas')
    metodo_pago = models.CharField(max_length=15, choices=METODOS_PAGO)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cliente_nombre = models.CharField(max_length=200, blank=True)
    cliente_nit = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Factura {self.numero_factura} - ${self.total}"

    def save(self, *args, **kwargs):
        """Genera el número de factura si no existe"""
        if not self.numero_factura:
            import datetime
            fecha_str = datetime.datetime.now().strftime('%Y%m%d')
            ultimo = Factura.objects.filter(numero_factura__startswith=f'F{fecha_str}').count()
            self.numero_factura = f'F{fecha_str}{str(ultimo + 1).zfill(4)}'
        super().save(*args, **kwargs)


class MovimientoCaja(models.Model):
    """Movimientos de caja detallados (entradas/salidas manuales)."""

    TIPO = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    )

    sesion = models.ForeignKey(
        CajaSesion,
        on_delete=models.CASCADE,
        related_name='movimientos',
    )
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TIPO)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=255)

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_caja',
    )

    class Meta:
        verbose_name = 'Movimiento de caja'
        verbose_name_plural = 'Movimientos de caja'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} - ${self.monto}"
