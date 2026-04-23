from django.db import models

from apps.core.models import Restaurante


class Categoria(models.Model):
    """Categorías de productos: bebidas, entradas, platos fuertes, postres, etc."""
    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='categorias_menu',
        help_text='Restaurante al que pertenece la categoría',
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
        unique_together = ('restaurante', 'nombre')
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    """Productos del menú del restaurante"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='productos')
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    tiempo_preparacion = models.IntegerField(help_text='Tiempo en minutos', default=15)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class MenuDiario(models.Model):
    """Menú corriente / del día"""
    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='menus_diarios',
        help_text='Restaurante al que pertenece el menú',
    )
    fecha = models.DateField()
    sopa = models.CharField(max_length=200, blank=True)
    caldos = models.TextField(blank=True, help_text='Lista separada por comas de caldos')
    principios = models.TextField(blank=True, help_text='Lista separada por comas')
    proteinas = models.TextField(blank=True, help_text='Lista separada por comas')
    acompanante = models.CharField(max_length=200, blank=True)
    limonada = models.CharField(max_length=200, blank=True)
    precio_sopa = models.DecimalField(max_digits=8, decimal_places=2, default=5000)
    precio_bandeja = models.DecimalField(max_digits=8, decimal_places=2, default=12000)
    precio_completo = models.DecimalField(max_digits=8, decimal_places=2, default=13000)
    # Configuración de desayuno del día
    desayuno_principales = models.TextField(blank=True, help_text='Lista separada por comas (desayuno)')
    desayuno_bebidas = models.TextField(blank=True, help_text='Lista separada por comas (desayuno)')
    desayuno_acompanante = models.CharField(max_length=200, blank=True)
    precio_desayuno = models.DecimalField(max_digits=8, decimal_places=2, default=8000)

    class Meta:
        verbose_name = 'Menú diario'
        verbose_name_plural = 'Menús diarios'
        ordering = ['-fecha']
        unique_together = ('restaurante', 'fecha')

    def __str__(self):
        return f"Menú {self.fecha}"


class RecetaProducto(models.Model):
    """Receta/base de consumo por cada unidad vendida de un producto."""

    producto = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        related_name='receta',
    )
    notas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Receta de producto'
        verbose_name_plural = 'Recetas de productos'
        ordering = ['producto__nombre']

    def __str__(self):
        return f"Receta - {self.producto.nombre}"


class RecetaIngrediente(models.Model):
    """Ingredientes consumidos por una unidad de producto."""

    receta = models.ForeignKey(
        RecetaProducto,
        on_delete=models.CASCADE,
        related_name='ingredientes',
    )
    ingrediente = models.ForeignKey(
        'inventario.Ingrediente',
        on_delete=models.CASCADE,
        related_name='recetas_producto',
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Cantidad consumida por una unidad vendida del producto.',
    )

    class Meta:
        verbose_name = 'Ingrediente de receta'
        verbose_name_plural = 'Ingredientes de receta'
        unique_together = ('receta', 'ingrediente')
        ordering = ['ingrediente__nombre']

    def __str__(self):
        return f"{self.receta.producto.nombre} -> {self.ingrediente.nombre} ({self.cantidad})"


class ConsumoOpcionMenu(models.Model):
    """Consumo de inventario para opciones elegibles del menú corriente/desayuno."""

    TIPOS_MENU = (
        ('corriente', 'Corriente'),
        ('desayuno', 'Desayuno'),
    )
    CATEGORIAS_OPCION = (
        ('sopa', 'Sopa'),
        ('principio', 'Principio'),
        ('proteina', 'Proteína'),
        ('acompanante', 'Acompañante'),
        ('principal', 'Principal'),
        ('bebida', 'Bebida'),
        ('caldo', 'Caldo'),
    )

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        related_name='consumos_menu',
    )
    tipo_menu = models.CharField(max_length=20, choices=TIPOS_MENU)
    categoria_opcion = models.CharField(max_length=20, choices=CATEGORIAS_OPCION)
    nombre_opcion = models.CharField(max_length=200)
    ingrediente = models.ForeignKey(
        'inventario.Ingrediente',
        on_delete=models.CASCADE,
        related_name='opciones_menu',
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Cantidad consumida por una unidad vendida al elegir esta opción.',
    )
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Consumo por opción de menú'
        verbose_name_plural = 'Consumos por opción de menú'
        ordering = ['tipo_menu', 'categoria_opcion', 'nombre_opcion', 'ingrediente__nombre']
        unique_together = (
            'restaurante',
            'tipo_menu',
            'categoria_opcion',
            'nombre_opcion',
            'ingrediente',
        )

    def __str__(self):
        return (
            f"{self.get_tipo_menu_display()} / {self.get_categoria_opcion_display()} / "
            f"{self.nombre_opcion} -> {self.ingrediente.nombre} ({self.cantidad})"
        )
