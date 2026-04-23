from rest_framework import viewsets, permissions
from apps.core.models import Restaurante
from .serializers import RestauranteSerializer

class RestauranteViewSet(viewsets.ModelViewSet):
    queryset = Restaurante.objects.all()
    serializer_class = RestauranteSerializer
    permission_classes = [permissions.IsAuthenticated]
