from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notificaciones', views.NotificacionViewSet, basename='notificacion')

urlpatterns = [
    path('login/', views.CustomAuthToken.as_view(), name='api_login'),
    path('me/', views.MeView.as_view(), name='api_me'),
    path('', include(router.urls)),
]
