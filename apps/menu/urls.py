from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='index'),
    path('corriente/', views.menu_corriente, name='corriente'),
    path('desayuno/', views.menu_desayuno, name='desayuno'),
    path('categorias/', views.categoria_list, name='categoria_lista'),
    path('categorias/nueva/', views.categoria_crear, name='categoria_nueva'),
    path('categorias/<int:categoria_id>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:categoria_id>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),
    path('nuevo/', views.producto_crear, name='nuevo'),
    path('<int:producto_id>/editar/', views.producto_editar, name='editar'),
    path('<int:producto_id>/eliminar/', views.producto_eliminar, name='eliminar'),
    
    # API Endpoints
    path('api/categorias/', views.categorias_list_json, name='api_categorias'),
    path('api/categorias/<int:categoria_id>/', views.categoria_detail_json, name='api_categorias_detail'),
    path('api/productos/', views.productos_list_json, name='api_productos'),
    path('api/productos/<int:producto_id>/', views.producto_detail_json, name='api_productos_detail'),
    path('api/menus-diarios/', views.menus_diarios_json, name='api_menus_diarios'),
    path('api/menus-diarios/<int:menu_id>/', views.menu_diario_detail_json, name='api_menus_diarios_detail'),
]
