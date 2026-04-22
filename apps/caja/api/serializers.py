from rest_framework import serializers
from apps.caja.models import CajaSesion, Factura, MovimientoCaja
from django.contrib.auth.models import User


class CajaSesionSerializer(serializers.ModelSerializer):
    usuario_apertura_nombre = serializers.CharField(source='usuario_apertura.get_full_name', read_only=True)
    usuario_cierre_nombre = serializers.CharField(source='usuario_cierre.get_full_name', read_only=True, allow_null=True)
    restaurante_nombre = serializers.CharField(source='restaurante.nombre', read_only=True, allow_null=True)
    
    class Meta:
        model = CajaSesion
        fields = [
            'id', 'restaurante', 'restaurante_nombre', 'usuario_apertura', 'usuario_apertura_nombre',
            'usuario_cierre', 'usuario_cierre_nombre', 'fecha_apertura', 'fecha_cierre',
            'estado', 'saldo_inicial', 'entradas_extra', 'salidas', 'saldo_final', 'observaciones',
        ]


class FacturaSerializer(serializers.ModelSerializer):
    cajero_nombre = serializers.CharField(source='cajero.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Factura
        fields = [
            'id', 'pedido', 'sesion', 'numero_factura', 'fecha', 'cajero', 'cajero_nombre',
            'metodo_pago', 'subtotal', 'impuesto', 'descuento', 'total',
            'cliente_nombre', 'cliente_nit',
        ]


class MovimientoCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoCaja
        fields = [
            'id', 'sesion', 'fecha', 'tipo', 'monto', 'concepto',
        ]
