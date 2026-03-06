from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Proveedor, TelefonoNegocio


def _get_restaurante_from_user(user):
    empleado = getattr(user, 'empleado', None)
    return getattr(empleado, 'restaurante', None) if empleado else None


def _user_is_admin(user):
    """Retorna True si el usuario es admin del sistema."""
    if user.is_superuser:
        return True
    empleado = getattr(user, 'empleado', None)
    rol = getattr(empleado, 'rol', None) if empleado else None
    nombre_rol = getattr(rol, 'nombre', '') if rol else ''
    return nombre_rol == 'admin'


@login_required(login_url='login')
def contactos_list(request):
    if not _user_is_admin(request.user):
        messages.error(request, 'Solo los administradores pueden gestionar contactos.')
        return redirect('dashboard')

    restaurante = _get_restaurante_from_user(request.user)

    proveedores_qs = Proveedor.objects.filter(activo=True)
    telefonos_qs = TelefonoNegocio.objects.filter(activo=True)

    if restaurante is not None:
        proveedores_qs = proveedores_qs.filter(restaurante=restaurante)
        telefonos_qs = telefonos_qs.filter(restaurante=restaurante)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'proveedor':
            nombre = request.POST.get('nombre', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            telefono_secundario = request.POST.get('telefono_secundario', '').strip()
            email = request.POST.get('email', '').strip()
            direccion = request.POST.get('direccion', '').strip()
            tipo = request.POST.get('tipo', '').strip() or 'otros'
            notas = request.POST.get('notas', '').strip()

            if not nombre:
                messages.error(request, 'El nombre del proveedor es obligatorio.')
            else:
                Proveedor.objects.create(
                    restaurante=restaurante,
                    nombre=nombre,
                    telefono=telefono,
                    telefono_secundario=telefono_secundario,
                    email=email or None,
                    direccion=direccion,
                    tipo=tipo,
                    notas=notas,
                )
                messages.success(request, 'Proveedor guardado correctamente.')
                return redirect('contactos:index')

        elif form_type == 'telefono':
            nombre = request.POST.get('nombre', '').strip()
            numero = request.POST.get('numero', '').strip()
            notas = request.POST.get('notas', '').strip()

            if not nombre or not numero:
                messages.error(request, 'Nombre y número son obligatorios para el teléfono del negocio.')
            else:
                TelefonoNegocio.objects.create(
                    restaurante=restaurante,
                    nombre=nombre,
                    numero=numero,
                    notas=notas,
                )
                messages.success(request, 'Teléfono del negocio guardado correctamente.')
                return redirect('contactos:index')

    context = {
        'active': 'contactos',
        'proveedores': proveedores_qs,
        'telefonos': telefonos_qs,
    }
    return render(request, 'contactos/contactos_list.html', context)


@login_required(login_url='login')
@require_POST
def proveedor_eliminar(request, proveedor_id):
    if not _user_is_admin(request.user):
        messages.error(request, 'No tienes permiso para eliminar proveedores.')
        return redirect('contactos:index')

    restaurante = _get_restaurante_from_user(request.user)
    proveedor = get_object_or_404(Proveedor, pk=proveedor_id, activo=True)

    if restaurante is not None and proveedor.restaurante_id is not None and proveedor.restaurante_id != restaurante.id:
        messages.error(request, 'No puedes eliminar proveedores de otro restaurante.')
        return redirect('contactos:index')

    proveedor.delete()
    messages.success(request, 'Proveedor eliminado correctamente.')
    return redirect('contactos:index')


@login_required(login_url='login')
def proveedor_editar(request, proveedor_id):
    if not _user_is_admin(request.user):
        messages.error(request, 'No tienes permiso para editar proveedores.')
        return redirect('contactos:index')

    restaurante = _get_restaurante_from_user(request.user)
    proveedor = get_object_or_404(Proveedor, pk=proveedor_id, activo=True)

    if restaurante is not None and proveedor.restaurante_id is not None and proveedor.restaurante_id != restaurante.id:
        messages.error(request, 'No puedes editar proveedores de otro restaurante.')
        return redirect('contactos:index')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        telefono_secundario = request.POST.get('telefono_secundario', '').strip()
        email = request.POST.get('email', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        tipo = request.POST.get('tipo', '').strip() or 'otros'
        notas = request.POST.get('notas', '').strip()

        if not nombre:
            messages.error(request, 'El nombre del proveedor es obligatorio.')
        else:
            proveedor.nombre = nombre
            proveedor.telefono = telefono
            proveedor.telefono_secundario = telefono_secundario
            proveedor.email = email or None
            proveedor.direccion = direccion
            proveedor.tipo = tipo
            proveedor.notas = notas
            proveedor.save()
            messages.success(request, 'Proveedor actualizado correctamente.')
            return redirect('contactos:index')

    context = {
        'active': 'contactos',
        'proveedor': proveedor,
    }
    return render(request, 'contactos/proveedor_form.html', context)


@login_required(login_url='login')
@require_POST
def telefono_eliminar(request, telefono_id):
    if not _user_is_admin(request.user):
        messages.error(request, 'No tienes permiso para eliminar teléfonos.')
        return redirect('contactos:index')

    restaurante = _get_restaurante_from_user(request.user)
    telefono = get_object_or_404(TelefonoNegocio, pk=telefono_id, activo=True)

    if restaurante is not None and telefono.restaurante_id is not None and telefono.restaurante_id != restaurante.id:
        messages.error(request, 'No puedes eliminar teléfonos de otro restaurante.')
        return redirect('contactos:index')

    telefono.delete()
    messages.success(request, 'Teléfono eliminado correctamente.')
    return redirect('contactos:index')


@login_required(login_url='login')
def telefono_editar(request, telefono_id):
    if not _user_is_admin(request.user):
        messages.error(request, 'No tienes permiso para editar teléfonos.')
        return redirect('contactos:index')

    restaurante = _get_restaurante_from_user(request.user)
    telefono = get_object_or_404(TelefonoNegocio, pk=telefono_id, activo=True)

    if restaurante is not None and telefono.restaurante_id is not None and telefono.restaurante_id != restaurante.id:
        messages.error(request, 'No puedes editar teléfonos de otro restaurante.')
        return redirect('contactos:index')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        numero = request.POST.get('numero', '').strip()
        notas = request.POST.get('notas', '').strip()

        if not nombre or not numero:
            messages.error(request, 'Nombre y número son obligatorios para el teléfono del negocio.')
        else:
            telefono.nombre = nombre
            telefono.numero = numero
            telefono.notas = notas
            telefono.save()
            messages.success(request, 'Teléfono actualizado correctamente.')
            return redirect('contactos:index')

    context = {
        'active': 'contactos',
        'telefono': telefono,
    }
    return render(request, 'contactos/telefono_form.html', context)
