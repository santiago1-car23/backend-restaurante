from django.contrib import admin

from .models import (
    Categoria,
    ConsumoOpcionMenu,
    Producto,
    RecetaIngrediente,
    RecetaProducto,
)


class RecetaIngredienteInline(admin.TabularInline):
    model = RecetaIngrediente
    extra = 1
    autocomplete_fields = ('ingrediente',)


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


@admin.register(RecetaProducto)
class RecetaProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'activo', 'actualizado_en')
    list_filter = ('activo',)
    search_fields = ('producto__nombre', 'notas')
    autocomplete_fields = ('producto',)
    inlines = [RecetaIngredienteInline]


@admin.register(ConsumoOpcionMenu)
class ConsumoOpcionMenuAdmin(admin.ModelAdmin):
    list_display = (
        'restaurante',
        'tipo_menu',
        'categoria_opcion',
        'nombre_opcion',
        'ingrediente',
        'cantidad',
        'activo',
    )
    list_filter = ('restaurante', 'tipo_menu', 'categoria_opcion', 'activo')
    search_fields = ('nombre_opcion', 'ingrediente__nombre')
    autocomplete_fields = ('ingrediente', 'restaurante')
