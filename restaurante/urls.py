"""
URL configuration for restaurante project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración de Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Restaurante API",
        default_version='v1',
        description="Documentación de API del sistema de restaurante",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contacto@restaurante.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Swagger UI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # API URLs
        path('api/', include('apps.api_urls')),

    # Apps URLs
    # Core sin namespace para poder usar 'dashboard' directamente
    path('', include('apps.core.urls')),

    # Autenticación de usuarios (sin namespace para mantener 'login'/'logout')
    path('usuarios/', include('apps.usuarios.urls')),

    # Resto de apps con namespace para usar 'app:index'
    path('menu/', include('apps.menu.urls', namespace='menu')),
    path('mesas/', include('apps.mesas.urls', namespace='mesas')),
    path('pedidos/', include('apps.pedidos.urls', namespace='pedidos')),
    path('caja/', include('apps.caja.urls', namespace='caja')),
    path('inventario/', include('apps.inventario.urls', namespace='inventario')),
    path('contactos/', include('apps.contactos.urls', namespace='contactos')),
    path('estadisticas/', include('apps.estadisticas.urls', namespace='estadisticas')),
    path('ajustes/', include('apps.ajustes.urls', namespace='ajustes')),
]
