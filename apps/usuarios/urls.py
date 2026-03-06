from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # API Endpoints
    path('api/empleados/', views.empleados_list_json, name='api_empleados'),
    path('api/empleados/<int:empleado_id>/', views.empleado_detail_json, name='api_empleados_detail'),
    path('api/roles/', views.roles_list_json, name='api_roles'),
    path('api/roles/<int:rol_id>/', views.rol_detail_json, name='api_roles_detail'),
]
