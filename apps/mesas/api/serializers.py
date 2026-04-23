from rest_framework import serializers

from apps.mesas.models import Mesa


class MesaSerializer(serializers.ModelSerializer):
    """Serializer para exponer mesas vía API REST.

    Incluye un campo de solo lectura con la representación legible del estado.
    """

    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    pedido_activo_id = serializers.SerializerMethodField()

    class Meta:
        model = Mesa
        fields = [
            'id',
            'restaurante',
            'numero',
            'capacidad',
            'estado',
            'estado_display',
            'pedido_activo_id',
            'ubicacion',
            'activa',
        ]
        read_only_fields = ['id']

    def get_pedido_activo_id(self, obj):
        pedido = obj.pedidos.filter(
            archivado=False,
            estado__in=['pendiente', 'en_preparacion', 'listo'],
        ).order_by('-fecha_creacion').first()
        return pedido.id if pedido else None
