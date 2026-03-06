from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from apps.usuarios.models import Empleado

from .forms import EmpleadoExtraForm, UsuarioForm


def _es_admin(user: User) -> bool:
    try:
        return bool(user.empleado and user.empleado.rol and user.empleado.rol.nombre == 'admin')
    except Empleado.DoesNotExist:
        return False


@login_required(login_url='login')
def usuario_list(request):
    if not _es_admin(request.user):
        return HttpResponseForbidden('No tienes permisos para acceder a esta sección.')

    restaurante = request.user.empleado.restaurante
    empleados = Empleado.objects.filter(restaurante=restaurante).select_related('user', 'rol')

    context = {
        'empleados': empleados,
    }
    return render(request, 'ajustes/usuarios_list.html', context)


@login_required(login_url='login')
def usuario_create(request):
    if not _es_admin(request.user):
        return HttpResponseForbidden('No tienes permisos para acceder a esta sección.')

    if request.method == 'POST':
        user_form = UsuarioForm(request.POST)
        empleado_form = EmpleadoExtraForm(request.POST)
        if user_form.is_valid() and empleado_form.is_valid():
            user = user_form.save(commit=False)
            pwd = user_form.cleaned_data.get('password1')
            if pwd:
                user.set_password(pwd)
            user.save()

            empleado = empleado_form.save(commit=False)
            empleado.user = user
            empleado.rol = user_form.cleaned_data['rol']
            empleado.restaurante = request.user.empleado.restaurante
            empleado.save()

            messages.success(request, 'Empleado creado correctamente.')
            return redirect('ajustes:usuarios_list')
    else:
        user_form = UsuarioForm()
        empleado_form = EmpleadoExtraForm()

    return render(request, 'ajustes/usuario_form.html', {
        'user_form': user_form,
        'empleado_form': empleado_form,
        'modo': 'crear',
    })


@login_required(login_url='login')
def usuario_update(request, pk: int):
    if not _es_admin(request.user):
        return HttpResponseForbidden('No tienes permisos para acceder a esta sección.')

    restaurante = request.user.empleado.restaurante
    empleado = get_object_or_404(Empleado, pk=pk, restaurante=restaurante)
    user = empleado.user

    if request.method == 'POST':
        user_form = UsuarioForm(request.POST, instance=user)
        empleado_form = EmpleadoExtraForm(request.POST, instance=empleado)
        if user_form.is_valid() and empleado_form.is_valid():
            user = user_form.save(commit=False)
            pwd = user_form.cleaned_data.get('password1')
            if pwd:
                user.set_password(pwd)
            user.save()

            empleado = empleado_form.save(commit=False)
            empleado.rol = user_form.cleaned_data['rol']
            empleado.save()

            messages.success(request, 'Empleado actualizado correctamente.')
            return redirect('ajustes:usuarios_list')
    else:
        initial = {'rol': empleado.rol}
        user_form = UsuarioForm(instance=user, initial=initial)
        empleado_form = EmpleadoExtraForm(instance=empleado)

    return render(request, 'ajustes/usuario_form.html', {
        'user_form': user_form,
        'empleado_form': empleado_form,
        'modo': 'editar',
        'empleado': empleado,
    })
