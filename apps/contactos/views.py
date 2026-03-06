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


# ============================================================================
# API ENDPOINTS CON SWAGGER
# ============================================================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


def _proveedor_payload(prov):
    return {
        'id': prov.id,
        'nombre': prov.nombre,
        'telefono': prov.telefono,
        'telefono_secundario': prov.telefono_secundario,
        'email': prov.email,
        'direccion': prov.direccion,
        'tipo': prov.tipo,
        'tipo_display': prov.get_tipo_display(),
        'notas': prov.notas,
        'activo': prov.activo,
    }


def _telefono_payload(tel):
    return {
        'id': tel.id,
        'nombre': tel.nombre,
        'numero': tel.numero,
        'notas': tel.notas,
        'activo': tel.activo,
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def proveedores_list_json(request):
    """API: Lista/crea proveedores."""
    restaurante = _get_restaurante_from_user(request.user)

    if request.method == 'POST':
        nombre = (request.data.get('nombre') or '').strip()
        if not nombre:
            return Response({'error': 'El nombre es obligatorio.'}, status=400)
        prov = Proveedor.objects.create(
            restaurante=restaurante,
            nombre=nombre,
            telefono=request.data.get('telefono', ''),
            telefono_secundario=request.data.get('telefono_secundario', ''),
            email=request.data.get('email') or None,
            direccion=request.data.get('direccion') or '',
            tipo=request.data.get('tipo', 'otros'),
            notas=request.data.get('notas', ''),
            activo=bool(request.data.get('activo', True)),
        )
        return Response({'proveedor': _proveedor_payload(prov)}, status=201)

    proveedores = Proveedor.objects.all()
    if restaurante and not request.user.is_superuser:
        proveedores = proveedores.filter(restaurante=restaurante)

    # Filtrar por tipo si se proporciona
    tipo = request.GET.get('tipo')
    if tipo:
        proveedores = proveedores.filter(tipo=tipo)

    # Filtrar por activo si se proporciona
    activo = request.GET.get('activo')
    if activo is not None:
        activo_bool = activo.lower() == 'true'
        proveedores = proveedores.filter(activo=activo_bool)

    return Response({'proveedores': [_proveedor_payload(prov) for prov in proveedores]})


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def proveedor_detail_json(request, proveedor_id):
    restaurante = _get_restaurante_from_user(request.user)
    prov = get_object_or_404(Proveedor, pk=proveedor_id)
    if restaurante and not request.user.is_superuser and prov.restaurante_id != getattr(restaurante, 'id', None):
        return Response({'error': 'No autorizado.'}, status=403)

    if request.method == 'DELETE':
        prov.delete()
        return Response(status=204)

    for field in ['nombre', 'telefono', 'telefono_secundario', 'email', 'direccion', 'tipo', 'notas']:
        if field in request.data:
            setattr(prov, field, request.data.get(field))
    if 'activo' in request.data:
        prov.activo = bool(request.data.get('activo'))
    prov.save()
    return Response({'proveedor': _proveedor_payload(prov)})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def telefonos_list_json(request):
    """API: Lista/crea teléfonos del negocio."""
    restaurante = _get_restaurante_from_user(request.user)

    if request.method == 'POST':
        nombre = (request.data.get('nombre') or '').strip()
        numero = (request.data.get('numero') or '').strip()
        if not nombre or not numero:
            return Response({'error': 'nombre y numero son obligatorios.'}, status=400)
        tel = TelefonoNegocio.objects.create(
            restaurante=restaurante,
            nombre=nombre,
            numero=numero,
            notas=request.data.get('notas', ''),
            activo=bool(request.data.get('activo', True)),
        )
        return Response({'telefono': _telefono_payload(tel)}, status=201)

    telefonos = TelefonoNegocio.objects.filter(activo=True)
    if restaurante and not request.user.is_superuser:
        telefonos = telefonos.filter(restaurante=restaurante)

    return Response({'telefonos': [_telefono_payload(tel) for tel in telefonos]})


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def telefono_detail_json(request, telefono_id):
    restaurante = _get_restaurante_from_user(request.user)
    tel = get_object_or_404(TelefonoNegocio, pk=telefono_id)
    if restaurante and not request.user.is_superuser and tel.restaurante_id != getattr(restaurante, 'id', None):
        return Response({'error': 'No autorizado.'}, status=403)

    if request.method == 'DELETE':
        tel.delete()
        return Response(status=204)

    for field in ['nombre', 'numero', 'notas']:
        if field in request.data:
            setattr(tel, field, request.data.get(field))
    if 'activo' in request.data:
        tel.activo = bool(request.data.get('activo'))
    tel.save()
    return Response({'telefono': _telefono_payload(tel)})
