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
]
