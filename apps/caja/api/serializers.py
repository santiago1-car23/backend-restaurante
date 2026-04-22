from rest_framework import serializers

from apps.caja.models import CajaSesion, Factura, MovimientoCaja


class CajaSesionSerializer(serializers.ModelSerializer):
    total_facturado = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    resultado_neto = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CajaSesion
        fields = [
            'id', 'restaurante', 'usuario_apertura', 'usuario_cierre',
            'fecha_apertura', 'fecha_cierre', 'estado',
            'saldo_inicial', 'entradas_extra', 'salidas', 'saldo_final',
            'observaciones', 'total_facturado', 'resultado_neto',
        ]
        read_only_fields = ['usuario_apertura', 'usuario_cierre', 'fecha_apertura', 'fecha_cierre', 'estado', 'saldo_final']


class FacturaSerializer(serializers.ModelSerializer):
    mesa_numero = serializers.SerializerMethodField()
    mesero_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Factura
        fields = [
            'id', 'numero_factura', 'pedido', 'sesion', 'fecha', 'cajero',
            'metodo_pago', 'subtotal', 'impuesto', 'descuento', 'total',
            'cliente_nombre', 'cliente_nit', 'mesa_numero', 'mesero_nombre',
        ]
        read_only_fields = ['numero_factura', 'fecha', 'subtotal', 'impuesto', 'descuento', 'total', 'cajero', 'sesion']

    def get_mesa_numero(self, obj):
        if obj.pedido and obj.pedido.mesa:
            return obj.pedido.mesa.numero
        return None

    def get_mesero_nombre(self, obj):
        if obj.pedido and obj.pedido.mesero:
            return obj.pedido.mesero.get_full_name() or obj.pedido.mesero.username
        return None


class MovimientoCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoCaja
        fields = ['id', 'sesion', 'fecha', 'tipo', 'monto', 'concepto', 'usuario']
        read_only_fields = ['fecha', 'usuario']


class AbrirCajaSerializer(serializers.Serializer):
    saldo_inicial = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    observaciones = serializers.CharField(allow_blank=True, required=False)


class CerrarCajaSerializer(serializers.Serializer):
    salidas = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    observaciones = serializers.CharField(allow_blank=True, required=False)


class RegistrarMovimientoSerializer(serializers.Serializer):
    valor = serializers.DecimalField(max_digits=10, decimal_places=2)
    descripcion = serializers.CharField(allow_blank=True, required=False)


class CobrarPedidoSerializer(serializers.Serializer):
    pedido_id = serializers.IntegerField()
    metodo_pago = serializers.ChoiceField(choices=Factura.METODOS_PAGO)
    cliente_nombre = serializers.CharField(allow_blank=True, required=False)
    cliente_nit = serializers.CharField(allow_blank=True, required=False)
