from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='index'),
    path('corriente/', views.menu_corriente, name='corriente'),
    path('desayuno/', views.menu_desayuno, name='desayuno'),
    path('recetas/', views.recetas_list, name='recetas'),
    path('recetas/<int:producto_id>/', views.receta_detalle, name='receta_detalle'),
    path('recetas/<int:producto_id>/ingredientes/<int:item_id>/eliminar/', views.receta_ingrediente_eliminar, name='receta_ingrediente_eliminar'),
    path('consumos-menu/', views.consumos_menu_list, name='consumos_menu'),
    path('consumos-menu/<int:item_id>/eliminar/', views.consumo_menu_eliminar, name='consumo_menu_eliminar'),
    path('categorias/', views.categoria_list, name='categoria_lista'),
    path('categorias/nueva/', views.categoria_crear, name='categoria_nueva'),
    path('categorias/<int:categoria_id>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:categoria_id>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),
    path('nuevo/', views.producto_crear, name='nuevo'),
    path('<int:producto_id>/editar/', views.producto_editar, name='editar'),
    path('<int:producto_id>/eliminar/', views.producto_eliminar, name='eliminar'),
]
