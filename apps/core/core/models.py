from django.db import models


class Restaurante(models.Model):
	"""Datos de cada restaurante/cliente que usa el sistema.

	Esta tabla permite arrendar el software a varios locales en la misma BD.
	"""

	nombre = models.CharField(max_length=200)
	nit = models.CharField(max_length=50, blank=True)
	codigo_cliente = models.CharField(
		max_length=50,
		unique=True,
		help_text="ID/licencia del restaurante dentro del sistema",
	)
	activo = models.BooleanField(default=True)

	fecha_inicio = models.DateField(null=True, blank=True)
	fecha_fin_licencia = models.DateField(null=True, blank=True)

	creado_en = models.DateTimeField(auto_now_add=True)
	actualizado_en = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Restaurante"
		verbose_name_plural = "Restaurantes"
		ordering = ["nombre"]

	def __str__(self) -> str:  # type: ignore[override]
		return f"{self.nombre} ({self.codigo_cliente})"

