from rest_framework import serializers

from apps.core.currency import formatear_pesos_colombianos
from apps.menu.models import (
    Categoria,
    ConsumoOpcionMenu,
    MenuDiario,
    Producto,
    RecetaIngrediente,
    RecetaProducto,
)


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = [
            'id',
            'nombre',
            'descripcion',
            'activo',
        ]
        read_only_fields = ['id']


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    precio_formateado = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'precio',
            'precio_formateado',
            'categoria',
            'categoria_nombre',
            'disponible',
            'tiempo_preparacion',
            'fecha_creacion',
        ]
        read_only_fields = ['id', 'fecha_creacion']

    def get_precio_formateado(self, obj):
        return formatear_pesos_colombianos(obj.precio)


class MenuDiarioSerializer(serializers.ModelSerializer):
    precio_sopa_formateado = serializers.SerializerMethodField()
    precio_bandeja_formateado = serializers.SerializerMethodField()
    precio_completo_formateado = serializers.SerializerMethodField()
    precio_desayuno_formateado = serializers.SerializerMethodField()

    class Meta:
        model = MenuDiario
        fields = [
            'id',
            'fecha',
            'sopa',
            'caldos',
            'principios',
            'proteinas',
            'acompanante',
            'limonada',
            'precio_sopa',
            'precio_sopa_formateado',
            'precio_bandeja',
            'precio_bandeja_formateado',
            'precio_completo',
            'precio_completo_formateado',
            'desayuno_principales',
            'desayuno_bebidas',
            'desayuno_acompanante',
            'precio_desayuno',
            'precio_desayuno_formateado',
        ]
        read_only_fields = ['id']

    def get_precio_sopa_formateado(self, obj):
        return formatear_pesos_colombianos(obj.precio_sopa)

    def get_precio_bandeja_formateado(self, obj):
        return formatear_pesos_colombianos(obj.precio_bandeja)

    def get_precio_completo_formateado(self, obj):
        return formatear_pesos_colombianos(obj.precio_completo)

    def get_precio_desayuno_formateado(self, obj):
        return formatear_pesos_colombianos(obj.precio_desayuno)


class RecetaIngredienteSerializer(serializers.ModelSerializer):
    ingrediente_nombre = serializers.CharField(source='ingrediente.nombre', read_only=True)
    ingrediente_unidad = serializers.CharField(source='ingrediente.unidad', read_only=True)

    class Meta:
        model = RecetaIngrediente
        fields = [
            'id',
            'ingrediente',
            'ingrediente_nombre',
            'ingrediente_unidad',
            'cantidad',
        ]
        read_only_fields = ['id']

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError('La cantidad/gramaje debe ser mayor que cero.')
        return value


class RecetaProductoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    ingredientes = RecetaIngredienteSerializer(many=True, read_only=True)

    class Meta:
        model = RecetaProducto
        fields = [
            'id',
            'producto',
            'producto_nombre',
            'notas',
            'activo',
            'ingredientes',
        ]
        read_only_fields = ['id']


class ConsumoOpcionMenuSerializer(serializers.ModelSerializer):
    ingrediente_nombre = serializers.CharField(source='ingrediente.nombre', read_only=True)
    ingrediente_unidad = serializers.CharField(source='ingrediente.unidad', read_only=True)

    class Meta:
        model = ConsumoOpcionMenu
        fields = [
            'id',
            'restaurante',
            'tipo_menu',
            'categoria_opcion',
            'nombre_opcion',
            'ingrediente',
            'ingrediente_nombre',
            'ingrediente_unidad',
            'cantidad',
            'activo',
        ]
        read_only_fields = ['id', 'restaurante']

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError('La cantidad/gramaje debe ser mayor que cero.')
        return value
