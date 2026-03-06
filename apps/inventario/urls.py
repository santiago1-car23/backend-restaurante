from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.inventario_list, name='index'),
    path('ingredientes/nuevo/', views.ingrediente_nuevo, name='ingrediente_nuevo'),
    path('ingredientes/<int:ingrediente_id>/editar/', views.ingrediente_editar, name='ingrediente_editar'),
    path('ingredientes/<int:ingrediente_id>/eliminar/', views.ingrediente_eliminar, name='ingrediente_eliminar'),
    path('movimientos/', views.movimientos_list, name='movimientos'),
    path('movimientos/nuevo/', views.movimiento_nuevo, name='movimiento_nuevo'),
    
    # API Endpoints
    path('api/ingredientes/', views.ingredientes_list_json, name='api_ingredientes'),
    path('api/ingredientes/<int:ingrediente_id>/', views.ingrediente_detail_json, name='api_ingredientes_detail'),
    path('api/movimientos/', views.movimientos_inventario_json, name='api_movimientos'),
    path('api/movimientos/<int:movimiento_id>/', views.movimiento_detail_json, name='api_movimientos_detail'),
]
