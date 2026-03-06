from django.urls import path
from . import views

app_name = 'caja'

urlpatterns = [
    path('', views.caja_view, name='index'),
    path('abrir/', views.abrir_caja, name='abrir_caja'),
    path('cerrar/', views.cerrar_caja, name='cerrar_caja'),
    path('cobrar/<int:pedido_id>/', views.cobrar_pedido, name='cobrar_pedido'),
    path('factura/<int:factura_id>/', views.factura_detalle, name='factura_detalle'),
    path('resumen/<int:sesion_id>/', views.resumen_caja, name='resumen_caja'),
    path('salida/', views.registrar_salida, name='registrar_salida'),
    path('entrada/', views.registrar_entrada, name='registrar_entrada'),
    path('venta-rapida/', views.venta_rapida, name='venta_rapida'),
    path('historial/', views.historial_caja, name='historial_caja'),
    
    # API Endpoints
    path('api/sesiones/', views.sesiones_caja_json, name='api_sesiones'),
    path('api/sesiones/<int:sesion_id>/', views.sesion_caja_detail_json, name='api_sesiones_detail'),
    path('api/facturas/', views.facturas_list_json, name='api_facturas'),
    path('api/facturas/<int:factura_id>/', views.factura_detail_json, name='api_facturas_detail'),
]
