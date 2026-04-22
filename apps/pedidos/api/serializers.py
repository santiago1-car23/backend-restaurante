from rest_framework import serializers
from apps.pedidos.models import Pedido, DetallePedido
from apps.menu.models import Producto


class ProductoInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio']


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto = ProductoInlineSerializer(read_only=True)
    
    class Meta:
        model = DetallePedido
        fields = [
            'id', 'pedido', 'producto', 'producto_nombre', 'cantidad',
            'precio_unitario', 'subtotal', 'observaciones', 'servido',
        ]


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    mesa_numero = serializers.IntegerField(source='mesa.numero', read_only=True)
    mesero_nombre = serializers.CharField(source='mesero.get_full_name', read_only=True, allow_null=True)
    restaurante_nombre = serializers.CharField(source='restaurante.nombre', read_only=True, allow_null=True)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'restaurante', 'restaurante_nombre', 'mesa', 'mesa_numero',
            'mesero', 'mesero_nombre', 'estado', 'fecha_creacion', 'fecha_actualizacion',
            'total', 'observaciones', 'archivado', 'detalles',
        ]
