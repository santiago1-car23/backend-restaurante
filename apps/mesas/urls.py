from django.urls import path
from . import views

app_name = 'mesas'

urlpatterns = [
    path('', views.mesas_list, name='index'),
    path('api/mesas/', views.mesas_list_json, name='lista_json'),
    path('crear/', views.mesa_crear, name='crear'),
    path('<int:mesa_id>/estado/', views.mesa_cambiar_estado, name='cambiar_estado'),
    path('<int:mesa_id>/eliminar/', views.mesa_eliminar, name='eliminar'),
]
