from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('service-worker.js', views.service_worker, name='service_worker'),
]
