"""
URL configuration for restaurante project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

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
