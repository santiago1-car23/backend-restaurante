from django.urls import path
from . import views

app_name = 'estadisticas'

urlpatterns = [
    path('mensual/', views.resumen_mensual, name='resumen_mensual'),
]
