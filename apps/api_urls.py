from apps.estadisticas.api import views as estadisticas_views
from apps.estadisticas.api.views import ResumenMensualView
from apps.core.api import views as core_views
from rest_framework.routers import DefaultRouter
from apps.ajustes.api import views as ajustes_views
from apps.caja.api import views as caja_views
from apps.caja.api.views import CajaSesionViewSet
from apps.contactos.api import views as contactos_views
from apps.inventario.api import views as inventario_views
from apps.menu.api import views as menu_views
from apps.mesas.api import views as mesas_views
from apps.pedidos.api import views as pedidos_views
from apps.usuarios.api import views as usuarios_views


router = DefaultRouter()

# Ajustes
router.register(r'ajustes/empleados', ajustes_views.EmpleadoViewSet, basename='ajustes-empleado')
router.register(r'ajustes/roles', ajustes_views.RolViewSet, basename='ajustes-rol')

# Caja
router.register(r'caja/sesiones', caja_views.CajaSesionViewSet, basename='caja-sesion')
router.register(r'caja/facturas', caja_views.FacturaViewSet, basename='caja-factura')
router.register(r'caja/movimientos', caja_views.MovimientoCajaViewSet, basename='caja-movimiento')

# Contactos
router.register(r'contactos/proveedores', contactos_views.ProveedorViewSet, basename='contactos-proveedor')
router.register(r'contactos/telefonos', contactos_views.TelefonoNegocioViewSet, basename='contactos-telefono')

# Inventario
router.register(r'inventario/ingredientes', inventario_views.IngredienteViewSet, basename='inventario-ingrediente')
router.register(r'inventario/movimientos', inventario_views.MovimientoInventarioViewSet, basename='inventario-movimiento')

# Menu
router.register(r'menu/categorias', menu_views.CategoriaViewSet, basename='menu-categoria')
router.register(r'menu/productos', menu_views.ProductoViewSet, basename='menu-producto')
router.register(r'menu/recetas', menu_views.RecetaProductoViewSet, basename='menu-receta')
router.register(r'menu/recetas-ingredientes', menu_views.RecetaIngredienteViewSet, basename='menu-receta-ingrediente')
router.register(r'menu/opciones-consumo', menu_views.ConsumoOpcionMenuViewSet, basename='menu-opcion-consumo')

# Mesas
router.register(r'mesas', mesas_views.MesaViewSet, basename='mesas')

# Pedidos
router.register(r'pedidos', pedidos_views.PedidoViewSet, basename='pedidos')
router.register(r'pedidos/detalles', pedidos_views.DetallePedidoViewSet, basename='pedido-detalle')

# Estadísticas
## Quitar registro de ResumenMensualView (APIView) del router
# router.register(r'estadisticas/resumen-mensual', estadisticas_views.ResumenMensualView, basename='resumen-mensual')

# Usuarios
router.register(r'usuarios/notificaciones', usuarios_views.NotificacionViewSet, basename='usuarios-notificacion')

# Core
router.register(r'restaurantes', core_views.RestauranteViewSet, basename='restaurante')

# Endpoints personalizados (no ViewSet):
from django.urls import path, include
urlpatterns = [
    path('', include(router.urls)),
    path('caja/sesion/activa/', CajaSesionViewSet.as_view({'get': 'activa'}), name='caja-sesion-activa'),
    path('estadisticas/resumen/', ResumenMensualView.as_view(), name='estadisticas-resumen'),
    path('menu-dia/', menu_views.MenuDiaView.as_view(), name='menu-dia'),
    path('me/', usuarios_views.MeView.as_view(), name='me'),
    path('usuarios/me/', usuarios_views.MeView.as_view(), name='usuarios-me'),
    path('auth/', usuarios_views.CustomAuthToken.as_view(), name='auth'),
    path('resumen-mensual/', estadisticas_views.ResumenMensualView.as_view(), name='resumen-mensual'),
]
