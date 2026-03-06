from django.contrib import admin
from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'disponible', 'tiempo_preparacion')
    list_filter = ('categoria', 'disponible', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('fecha_creacion',)
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'categoria', 'descripcion')
        }),
        ('Precios y Disponibilidad', {
            'fields': ('precio', 'disponible')
        }),
        ('Preparación', {
            'fields': ('tiempo_preparacion',)
        }),
        ('Imagen', {
            'fields': ('imagen',)
        }),
        ('Fecha', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
