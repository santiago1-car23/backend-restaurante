from django.contrib import admin
from .models import Ingrediente, MovimientoInventario

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad_actual', 'cantidad_minima', 'alerta_stock')
    list_filter = ('unidad',)
    search_fields = ('nombre',)
    fieldsets = (
        ('Información', {
            'fields': ('nombre', 'unidad')
        }),
        ('Stock', {
            'fields': ('cantidad_actual', 'cantidad_minima')
        }),
        ('Costo', {
            'fields': ('costo_unitario',)
        }),
    )

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('ingrediente', 'tipo', 'cantidad', 'fecha', 'usuario')
    list_filter = ('tipo', 'fecha', 'ingrediente')
    search_fields = ('ingrediente__nombre', 'motivo')
    readonly_fields = ('fecha',)
    fieldsets = (
        ('Movimiento', {
            'fields': ('ingrediente', 'tipo', 'cantidad')
        }),
        ('Detalles', {
            'fields': ('motivo', 'usuario')
        }),
        ('Fecha', {
            'fields': ('fecha',),
            'classes': ('collapse',)
        }),
    )
