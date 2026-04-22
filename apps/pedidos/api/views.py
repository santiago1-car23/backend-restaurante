from rest_framework import viewsets, permissions
from apps.pedidos.models import Pedido, DetallePedido
from .serializers import PedidoSerializer, DetallePedidoSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar pedidos"""
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]


class DetallePedidoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar detalles de pedidos"""
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
    permission_classes = [permissions.IsAuthenticated]
