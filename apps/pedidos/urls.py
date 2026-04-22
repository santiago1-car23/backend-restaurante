from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    # Lista principal de pedidos
    path('', views.lista_pedidos, name='lista'),
    path('api/ordenes/', views.lista_pedidos_json, name='lista_json'),
    path('<int:orden_id>/', views.detalle_pedido, name='detalle'),
    path('<int:orden_id>/productos-partial/', views.detalle_pedido_productos_partial, name='detalle_productos_partial'),
    path('<int:orden_id>/editar/', views.editar_pedido, name='editar'),
    path('<int:orden_id>/eliminar/', views.eliminar_pedido, name='eliminar'),
    path('detalle/<int:detalle_id>/servido/', views.marcar_detalle_servido, name='detalle_servido'),
]
