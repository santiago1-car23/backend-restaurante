from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    # Lista principal de pedidos
    path('', views.lista_pedidos, name='lista'),
    path('api/ordenes/', views.lista_pedidos_json, name='lista_json'),
    path('api/ordenes/<int:orden_id>/', views.pedido_detail_json, name='detalle_json'),
    path('<int:orden_id>/', views.detalle_pedido, name='detalle'),
    path('<int:orden_id>/parcial/', views.detalle_pedido_parcial, name='detalle_parcial'),
    path('<int:orden_id>/editar/', views.editar_pedido, name='editar'),
    path('<int:orden_id>/eliminar/', views.eliminar_pedido, name='eliminar'),
    path('detalle/<int:detalle_id>/servido/', views.marcar_detalle_servido, name='detalle_servido'),
]
