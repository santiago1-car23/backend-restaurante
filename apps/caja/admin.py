from django.contrib import admin
from .models import Factura


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'pedido', 'fecha', 'metodo_pago', 'total')
    list_filter = ('metodo_pago', 'fecha')
    search_fields = ('numero_factura', 'cliente_nit', 'cliente_nombre')
    readonly_fields = ('numero_factura', 'fecha')
    fieldsets = (
        ('Factura', {
            'fields': ('numero_factura', 'pedido')
        }),
        ('Datos del Cliente', {
            'fields': ('cliente_nombre', 'cliente_nit')
        }),
        ('Dinero', {
            'fields': ('metodo_pago', 'subtotal', 'impuesto', 'descuento', 'total')
        }),
        ('Cajer@', {
            'fields': ('cajero',)
        }),
        ('Fecha', {
            'fields': ('fecha',),
            'classes': ('collapse',)
        }),
    )
