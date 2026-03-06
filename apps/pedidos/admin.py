from django.contrib import admin
from .models import Pedido, DetallePedido

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    readonly_fields = ('subtotal',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal', 'observaciones')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'mesa', 'mesero', 'estado', 'total', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion', 'mesa')
    search_fields = ('mesa__numero', 'mesero__username', 'id')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'total')
    inlines = [DetallePedidoInline]
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('id', 'mesa', 'mesero')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Total', {
            'fields': ('total',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('pedido__fecha_creacion', 'producto')
    search_fields = ('pedido__id', 'producto__nombre')
    readonly_fields = ('subtotal',)
