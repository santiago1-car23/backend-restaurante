from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form, 'active': 'login'})

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')


# ============================================================================
# API ENDPOINTS CON SWAGGER
# ============================================================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


def _empleado_payload(emp):
    return {
        'id': emp.id,
        'usuario': emp.user.username,
        'nombre_completo': emp.user.get_full_name(),
        'email': emp.user.email,
        'rol': emp.rol.nombre if emp.rol else None,
        'rol_display': emp.rol.get_nombre_display() if emp.rol else None,
        'telefono': emp.telefono,
        'activo': emp.activo,
        'fecha_contratacion': emp.fecha_contratacion.isoformat() if emp.fecha_contratacion else None,
    }


def _rol_payload(rol):
    return {
        'id': rol.id,
        'nombre': rol.nombre,
        'nombre_display': rol.get_nombre_display(),
        'descripcion': rol.descripcion,
        'total_empleados': rol.empleados.count(),
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def empleados_list_json(request):
    """API: Lista/crea empleados."""
    from .models import Empleado, Rol
    from django.contrib.auth.models import User

    if request.method == 'POST':
        username = (request.data.get('username') or '').strip()
        password = request.data.get('password') or '123456'
        if not username:
            return Response({'error': 'username es obligatorio.'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'El username ya existe.'}, status=400)
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=request.data.get('first_name', ''),
            last_name=request.data.get('last_name', ''),
            email=request.data.get('email', ''),
        )
        rol = None
        rol_id = request.data.get('rol_id')
        if rol_id:
            rol = get_object_or_404(Rol, pk=rol_id)
        emp = Empleado.objects.create(
            user=user,
            rol=rol,
            telefono=request.data.get('telefono', ''),
            direccion=request.data.get('direccion', ''),
            activo=bool(request.data.get('activo', True)),
        )
        return Response({'empleado': _empleado_payload(emp)}, status=201)

    empleados = Empleado.objects.select_related('user', 'rol', 'restaurante').all()

    # Filtrar por activo si se proporciona
    activo = request.GET.get('activo')
    if activo is not None:
        activo_bool = activo.lower() == 'true'
        empleados = empleados.filter(activo=activo_bool)

    return Response({'empleados': [_empleado_payload(emp) for emp in empleados]})


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def empleado_detail_json(request, empleado_id):
    from .models import Empleado, Rol

    emp = get_object_or_404(Empleado.objects.select_related('user', 'rol'), pk=empleado_id)
    if request.method == 'DELETE':
        emp.user.delete()
        return Response(status=204)

    if 'rol_id' in request.data:
        emp.rol = get_object_or_404(Rol, pk=request.data.get('rol_id'))
    if 'telefono' in request.data:
        emp.telefono = request.data.get('telefono')
    if 'direccion' in request.data:
        emp.direccion = request.data.get('direccion')
    if 'activo' in request.data:
        emp.activo = bool(request.data.get('activo'))
    if 'first_name' in request.data:
        emp.user.first_name = request.data.get('first_name') or ''
    if 'last_name' in request.data:
        emp.user.last_name = request.data.get('last_name') or ''
    if 'email' in request.data:
        emp.user.email = request.data.get('email') or ''
    emp.user.save()
    emp.save()
    return Response({'empleado': _empleado_payload(emp)})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def roles_list_json(request):
    """API: Lista/crea roles del sistema."""
    from .models import Rol

    if request.method == 'POST':
        nombre = (request.data.get('nombre') or '').strip()
        if not nombre:
            return Response({'error': 'nombre es obligatorio.'}, status=400)
        if Rol.objects.filter(nombre=nombre).exists():
            return Response({'error': 'El rol ya existe.'}, status=400)
        rol = Rol.objects.create(nombre=nombre, descripcion=request.data.get('descripcion', ''))
        return Response({'rol': _rol_payload(rol)}, status=201)

    roles = Rol.objects.all()

    return Response({'roles': [_rol_payload(rol) for rol in roles]})


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def rol_detail_json(request, rol_id):
    from .models import Rol

    rol = get_object_or_404(Rol, pk=rol_id)
    if request.method == 'DELETE':
        rol.delete()
        return Response(status=204)

    if 'nombre' in request.data:
        rol.nombre = request.data.get('nombre')
    if 'descripcion' in request.data:
        rol.descripcion = request.data.get('descripcion')
    rol.save()
    return Response({'rol': _rol_payload(rol)})

