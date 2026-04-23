from rest_framework import serializers
from apps.core.models import Restaurante

class RestauranteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurante
        fields = ['id', 'nombre', 'nit', 'codigo_cliente', 'activo', 'fecha_inicio', 'fecha_fin_licencia']
