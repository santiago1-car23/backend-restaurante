from rest_framework import serializers

from apps.inventario.models import Ingrediente, MovimientoInventario


class IngredienteSerializer(serializers.ModelSerializer):
    alerta_stock = serializers.SerializerMethodField()

    class Meta:
        model = Ingrediente
        fields = [
            'id', 'restaurante', 'nombre', 'unidad', 'cantidad_actual',
            'cantidad_minima', 'costo_unitario', 'alerta_stock',
        ]
        read_only_fields = ['restaurante']

    def get_alerta_stock(self, obj):
        return obj.alerta_stock()


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    ingrediente_nombre = serializers.CharField(source='ingrediente.nombre', read_only=True)

    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'ingrediente', 'ingrediente_nombre', 'tipo', 'cantidad',
            'fecha', 'motivo', 'usuario',
        ]
        read_only_fields = ['fecha', 'usuario']


class RegistrarMovimientoSerializer(serializers.Serializer):
    ingrediente_id = serializers.IntegerField()
    tipo = serializers.ChoiceField(choices=MovimientoInventario.TIPOS)
    cantidad = serializers.DecimalField(max_digits=10, decimal_places=2)
    motivo = serializers.CharField(max_length=200)

    def validate(self, attrs):
        from apps.inventario.models import Ingrediente

        request = self.context['request']
        empleado = getattr(request.user, 'empleado', None)
        restaurante = getattr(empleado, 'restaurante', None) if empleado else None

        try:
            if restaurante and not request.user.is_superuser:
                ingrediente = Ingrediente.objects.get(id=attrs['ingrediente_id'], restaurante=restaurante)
            else:
                ingrediente = Ingrediente.objects.get(id=attrs['ingrediente_id'])
        except Ingrediente.DoesNotExist:
            raise serializers.ValidationError({'ingrediente_id': 'Ingrediente no encontrado para este restaurante.'})

        attrs['ingrediente'] = ingrediente
        return attrs
