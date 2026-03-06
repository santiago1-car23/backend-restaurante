from django.urls import path

from . import views

app_name = 'contactos'

urlpatterns = [
    path('', views.contactos_list, name='index'),
    path('proveedor/<int:proveedor_id>/editar/', views.proveedor_editar, name='proveedor_editar'),
    path('proveedor/<int:proveedor_id>/eliminar/', views.proveedor_eliminar, name='proveedor_eliminar'),
    path('telefono/<int:telefono_id>/editar/', views.telefono_editar, name='telefono_editar'),
    path('telefono/<int:telefono_id>/eliminar/', views.telefono_eliminar, name='telefono_eliminar'),
]
