from django.contrib import admin

from .models import Restaurante


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
	list_display = ("nombre", "codigo_cliente", "nit", "activo")
	list_filter = ("activo",)
	search_fields = ("nombre", "codigo_cliente", "nit")
