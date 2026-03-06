"""
Sistema de permisos por rol para controlar acceso a módulos.
"""
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def obtener_rol_usuario(user):
    """Obtiene el rol del usuario de forma segura."""
    if not user.is_authenticated:
        return None
    
    # Superusuarios y staff tienen acceso total
    if user.is_superuser or user.is_staff:
        return 'admin'
    
    empleado = getattr(user, 'empleado', None)
    if not empleado:
        return None
    
    rol = getattr(empleado, 'rol', None)
    if not rol:
        return None
    
    return getattr(rol, 'nombre', '').lower()


# Definir permisos por módulo
PERMISOS_MODULOS = {
    'caja': ['admin', 'cajero', 'administrador', 'gerente'],
}


def tiene_permiso_modulo(user, modulo):
    """
    Verifica si el usuario tiene permiso para acceder a un módulo.
    
    Args:
        user: Usuario de Django
        modulo: Nombre del módulo ('caja', 'menu', 'pedidos', etc.)
    
    Returns:
        bool: True si tiene permiso, False en caso contrario
    """
    if not user.is_authenticated:
        return False
    
    # Superusuarios siempre tienen acceso
    if user.is_superuser:
        return True
    
    # Staff (administradores de Django) tienen acceso
    if user.is_staff:
        return True
    
    rol = obtener_rol_usuario(user)
    if not rol:
        return False
    
    roles_permitidos = PERMISOS_MODULOS.get(modulo, [])
    return rol in roles_permitidos


def requiere_permiso(modulo, mensaje_error=None):
    """
    Decorador para proteger vistas por rol.
    
    Uso:
        @requiere_permiso('caja')
        def mi_vista(request):
            ...
    """
    def decorador(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not tiene_permiso_modulo(request.user, modulo):
                if mensaje_error:
                    messages.error(request, mensaje_error)
                else:
                    messages.error(request, f'No tienes permisos para acceder a {modulo}.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorador
