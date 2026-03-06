from django.urls import path
from . import views

app_name = 'ajustes'

urlpatterns = [
    path('usuarios/', views.usuario_list, name='usuarios_list'),
    path('usuarios/nuevo/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.usuario_update, name='usuario_update'),
]
