from django.contrib import admin
from .models import Rol, Empleado

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'restaurante', 'telefono', 'hora_entrada', 'hora_salida', 'activo', 'fecha_contratacion')
    list_filter = ('rol', 'restaurante', 'activo', 'fecha_contratacion')
    search_fields = ('user__username', 'user__first_name', 'telefono')
    readonly_fields = ('fecha_contratacion',)
    fieldsets = (
        ('Información de Usuario', {
            'fields': ('user', 'rol', 'restaurante')
        }),
        ('Datos de Contacto', {
            'fields': ('telefono', 'direccion')
        }),
        ('Empleo', {
            'fields': ('hora_entrada', 'hora_salida', 'activo', 'fecha_contratacion')
        }),
    )
