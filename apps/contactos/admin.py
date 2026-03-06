from django.contrib import admin

from .models import Proveedor, TelefonoNegocio


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'tipo', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('nombre', 'telefono', 'email')


@admin.register(TelefonoNegocio)
class TelefonoNegocioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'numero', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'numero')
