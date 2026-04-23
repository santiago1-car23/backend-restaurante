from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from apps.usuarios.models import Notificacion
from .serializers import UserProfileSerializer, NotificacionSerializer


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserProfileSerializer(user)
        return Response({
            'token': token.key,
            'user': user_serializer.data
        })


class MeView(APIView):
    """Devuelve el perfil del usuario autenticado, incluyendo su empleado y rol."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """Notificaciones del usuario autenticado."""

    serializer_class = NotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user).order_by('-creada')

    @action(detail=True, methods=['post'], url_path='marcar-leida')
    def marcar_leida(self, request, pk=None):
        notificacion = self.get_object()
        notificacion.leida = True
        notificacion.save(update_fields=['leida'])
        return Response(NotificacionSerializer(notificacion).data)

    @action(detail=False, methods=['post'], url_path='marcar-todas-leidas')
    def marcar_todas_leidas(self, request):
        qs = self.get_queryset().filter(leida=False)
        qs.update(leida=True)
        return Response({'marcadas': qs.count()}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='no-leidas-count')
    def no_leidas_count(self, request):
        count = self.get_queryset().filter(leida=False).count()
        return Response({'count': count}, status=status.HTTP_200_OK)
