from rest_framework import viewsets, permissions
from apps.caja.models import CajaSesion, Factura, MovimientoCaja
from .serializers import CajaSesionSerializer, FacturaSerializer, MovimientoCajaSerializer


class CajaSesionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar sesiones de caja"""
    queryset = CajaSesion.objects.all()
    serializer_class = CajaSesionSerializer
    permission_classes = [permissions.IsAuthenticated]


class FacturaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar facturas"""
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = [permissions.IsAuthenticated]


class MovimientoCajaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar movimientos de caja"""
    queryset = MovimientoCaja.objects.all()
    serializer_class = MovimientoCajaSerializer
    permission_classes = [permissions.IsAuthenticated]
