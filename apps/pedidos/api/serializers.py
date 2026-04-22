from rest_framework import serializers

from apps.core.currency import formatear_pesos_colombianos
from apps.menu.inventario import (
    construir_consumos_receta_producto,
    validar_stock_consumos,
)
from apps.pedidos.models import Pedido, DetallePedido


def _detalle_tiene_stock_suficiente(producto, restaurante, cantidad_requerida):
    from apps.inventario.models import Ingrediente

    ingredientes_qs = Ingrediente.objects.filter(nombre=producto.nombre)
    if restaurante:
        ingredientes_qs = ingredientes_qs.filter(restaurante=restaurante)

    ingrediente = ingredientes_qs.first()
    disponible = ingrediente.cantidad_actual if ingrediente else 0
    return ingrediente, disponible >= cantidad_requerida


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    precio_unitario_formateado = serializers.SerializerMethodField()
    subtotal_formateado = serializers.SerializerMethodField()

    class Meta:
        model = DetallePedido
        fields = [
            'id',
            'pedido',
            'producto',
            'producto_nombre',
            'cantidad',
            'precio_unitario',
            'precio_unitario_formateado',
            'subtotal',
            'subtotal_formateado',
            'observaciones',
            'servido',
        ]
        read_only_fields = ['id', 'subtotal', 'pedido']

    def get_precio_unitario_formateado(self, obj):
        return formatear_pesos_colombianos(obj.precio_unitario)

    def get_subtotal_formateado(self, obj):
        return formatear_pesos_colombianos(obj.subtotal)


class PedidoSerializer(serializers.ModelSerializer):
    mesa_numero = serializers.IntegerField(source='mesa.numero', read_only=True)
    mesero_nombre = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    hora = serializers.SerializerMethodField()
    tiene_factura = serializers.SerializerMethodField()
    factura_id = serializers.SerializerMethodField()
    total_formateado = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = [
            'id',
            'restaurante',
            'mesa',
            'mesa_numero',
            'mesero',
            'mesero_nombre',
            'estado',
            'estado_display',
            'fecha_creacion',
            'fecha_actualizacion',
            'hora',
            'total',
            'total_formateado',
            'observaciones',
            'archivado',
            'tiene_factura',
            'factura_id',
            'detalles',
        ]
        read_only_fields = [
            'id',
            'restaurante',
            'mesero',
            'fecha_creacion',
            'fecha_actualizacion',
            'hora',
            'total',
            'archivado',
            'tiene_factura',
            'factura_id',
        ]

    def get_mesero_nombre(self, obj):
        user = obj.mesero
        if not user:
            return ''
        full = user.get_full_name()
        return full or user.username

    def get_hora(self, obj):
        return obj.fecha_creacion.strftime('%H:%M') if obj.fecha_creacion else ''

    def get_tiene_factura(self, obj):
        return hasattr(obj, 'factura')

    def get_factura_id(self, obj):
        factura = getattr(obj, 'factura', None)
        return factura.id if factura else None

    def get_total_formateado(self, obj):
        return formatear_pesos_colombianos(obj.total)


class CrearPedidoSerializer(serializers.Serializer):
    """Abre un nuevo pedido desde una mesa libre."""

    mesa_id = serializers.IntegerField()
    observaciones = serializers.CharField(required=False, allow_blank=True)

    def validate_mesa_id(self, value):
        from apps.mesas.models import Mesa

        try:
            mesa = Mesa.objects.get(pk=value, activa=True)
        except Mesa.DoesNotExist:
            raise serializers.ValidationError('La mesa no existe o no está activa.')

        if mesa.estado != 'libre':
            raise serializers.ValidationError('La mesa no está libre para abrir un pedido.')

        tiene_activo = mesa.pedidos.filter(
            archivado=False,
            estado__in=['pendiente', 'en_preparacion', 'listo'],
        ).exists()
        if tiene_activo:
            raise serializers.ValidationError('La mesa ya tiene un pedido activo.')

        self.context['mesa'] = mesa
        return value

    def create(self, validated_data):
        request = self.context['request']
        mesa = self.context['mesa']

        empleado = getattr(request.user, 'empleado', None)
        restaurante = getattr(empleado, 'restaurante', None) if empleado else None
        if restaurante and mesa.restaurante_id != getattr(restaurante, 'id', None):
            raise serializers.ValidationError('La mesa no pertenece a tu restaurante.')

        pedido = Pedido.objects.create(
            mesa=mesa,
            mesero=request.user,
            restaurante=mesa.restaurante,
            estado='pendiente',
            observaciones=(validated_data.get('observaciones') or '').strip(),
        )
        mesa.estado = 'ocupada'
        mesa.save(update_fields=['estado'])
        return pedido


class CrearDetallePedidoSerializer(serializers.Serializer):
    """Agrega producto general a un pedido existente."""

    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1, default=1)
    observaciones = serializers.CharField(allow_blank=True, required=False)

    def validate(self, attrs):
        from apps.menu.models import Producto

        pedido = self.context['pedido']
        restaurante = getattr(pedido, 'restaurante', None)

        try:
            producto = Producto.objects.get(pk=attrs['producto_id'], disponible=True)
        except Producto.DoesNotExist:
            raise serializers.ValidationError({'producto_id': 'Producto no encontrado o no disponible.'})

        if restaurante and getattr(producto.categoria, 'restaurante_id', None) not in [None, restaurante.id]:
            raise serializers.ValidationError({'producto_id': 'El producto no pertenece a tu restaurante.'})

        consumos_por_unidad = construir_consumos_receta_producto(producto)
        if consumos_por_unidad:
            errores = validar_stock_consumos(restaurante, consumos_por_unidad, attrs['cantidad'])
            if errores:
                raise serializers.ValidationError(' '.join(errores))
        else:
            _, hay_stock = _detalle_tiene_stock_suficiente(producto, restaurante, attrs['cantidad'])
            if not hay_stock:
                raise serializers.ValidationError('No hay stock suficiente para este producto.')

        attrs['producto'] = producto
        attrs['consumos_inventario'] = consumos_por_unidad
        return attrs

    def create(self, validated_data):
        pedido = self.context['pedido']
        producto = validated_data['producto']
        cantidad = validated_data['cantidad']
        observaciones = validated_data.get('observaciones', '').strip()

        return DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio,
            observaciones=observaciones,
            consumos_inventario=validated_data.get('consumos_inventario', []),
        )


class ActualizarPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['estado', 'observaciones']


class ActualizarDetallePedidoSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField(required=False)
    cantidad = serializers.IntegerField(required=False, min_value=1)
    observaciones = serializers.CharField(required=False, allow_blank=True)
    servido = serializers.BooleanField(required=False)

    def validate(self, attrs):
        from apps.menu.models import Producto

        detalle = self.context['detalle']
        pedido = detalle.pedido
        restaurante = getattr(pedido, 'restaurante', None)

        producto = detalle.producto
        if 'producto_id' in attrs:
            try:
                producto = Producto.objects.get(pk=attrs['producto_id'], disponible=True)
            except Producto.DoesNotExist:
                raise serializers.ValidationError({'producto_id': 'Producto no encontrado o no disponible.'})

        cantidad = attrs.get('cantidad', detalle.cantidad)
        cantidad_a_validar = cantidad
        consumos_por_unidad = construir_consumos_receta_producto(producto)
        if consumos_por_unidad:
            cantidad_validar_receta = cantidad
            if producto.id == detalle.producto_id and detalle.consumos_inventario:
                cantidad_validar_receta = max(cantidad - detalle.cantidad, 0)
            errores = validar_stock_consumos(restaurante, consumos_por_unidad, cantidad_validar_receta)
            if errores:
                raise serializers.ValidationError(' '.join(errores))
        else:
            if producto.id == detalle.producto_id:
                cantidad_a_validar = max(cantidad - detalle.cantidad, 0)

            _, hay_stock = _detalle_tiene_stock_suficiente(producto, restaurante, cantidad_a_validar)
            if cantidad_a_validar > 0 and not hay_stock:
                raise serializers.ValidationError('No hay stock suficiente para actualizar este detalle.')

        attrs['producto'] = producto
        attrs['cantidad_final'] = cantidad
        attrs['consumos_inventario'] = consumos_por_unidad
        return attrs

    def update(self, instance, validated_data):
        producto = validated_data.get('producto', instance.producto)
        instance.producto = producto
        instance.precio_unitario = producto.precio
        instance.cantidad = validated_data.get('cantidad_final', instance.cantidad)
        instance.consumos_inventario = validated_data.get('consumos_inventario', instance.consumos_inventario)

        if 'observaciones' in validated_data:
            instance.observaciones = validated_data.get('observaciones', '').strip()

        if 'servido' in validated_data:
            instance.servido = validated_data['servido']

        instance.save()
        return instance
