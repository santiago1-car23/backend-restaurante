from django.contrib import admin
from .models import Mesa

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'capacidad', 'estado', 'ubicacion', 'activa')
    list_filter = ('estado', 'activa', 'ubicacion')
    search_fields = ('numero', 'ubicacion')
    fieldsets = (
        ('Identificación', {
            'fields': ('numero', 'ubicacion')
        }),
        ('Capacidad y Estado', {
            'fields': ('capacidad', 'estado')
        }),
        ('Disponibilidad', {
            'fields': ('activa',)
        }),
    )
