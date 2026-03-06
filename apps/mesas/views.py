from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .models import Mesa

@login_required(login_url='login')
def mesas_list(request):
    estado = request.GET.get('estado')

    # Detectar restaurante del empleado (si está configurado)
    empleado = getattr(request.user, 'empleado', None)
    restaurante = getattr(empleado, 'restaurante', None) if empleado else None

    mesas = Mesa.objects.filter(activa=True)
    if restaurante is not None:
        mesas = mesas.filter(restaurante=restaurante)
    
    if estado:
        mesas = mesas.filter(estado=estado)
    
    context = {
        'active': 'mesas',
        'mesas': mesas,
        'estado': estado,
        'estados': Mesa.ESTADOS,
    }
    return render(request, 'mesas/mesas_list.html', context)


@login_required(login_url='login')
def mesas_list_json(request):
    """Devuelve el estado actual de las mesas activas para refresco en vivo."""
    estado = request.GET.get('estado')
    empleado = getattr(request.user, 'empleado', None)
    restaurante = getattr(empleado, 'restaurante', None) if empleado else None

    qs = Mesa.objects.filter(activa=True)
    if restaurante is not None:
        qs = qs.filter(restaurante=restaurante)
    if estado:
        qs = qs.filter(estado=estado)

    mesas_data = [
        {
            'id': m.id,
            'numero': m.numero,
            'capacidad': m.capacidad,
            'estado': m.estado,
            'estado_display': m.get_estado_display(),
        }
        for m in qs.order_by('numero')
    ]

    return JsonResponse({'mesas': mesas_data})


@login_required(login_url='login')
@require_POST
def mesa_crear(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para crear mesas.')
        return redirect('mesas:index')

    numero = request.POST.get('numero')
    capacidad = request.POST.get('capacidad') or 4
    ubicacion = request.POST.get('ubicacion', '').strip()

    try:
        numero_int = int(numero) if numero else None
        capacidad_int = int(capacidad) if capacidad else 4
    except ValueError:
        messages.error(request, 'Datos inválidos: usa números válidos.')
        return redirect('mesas:index')

    if numero_int is None or numero_int < 1:
        messages.error(request, 'El número de mesa debe ser mayor o igual a 1.')
        return redirect('mesas:index')

    if capacidad_int < 1:
        messages.error(request, 'La capacidad debe ser al menos 1.')
        return redirect('mesas:index')

    empleado = getattr(request.user, 'empleado', None)
    restaurante = getattr(empleado, 'restaurante', None) if empleado else None

    qs = Mesa.objects.filter(activa=True, numero=numero_int)
    if restaurante is not None:
        qs = qs.filter(restaurante=restaurante)

    if qs.exists():
        messages.error(request, f'La mesa #{numero_int} ya existe para este restaurante.')
        return redirect('mesas:index')

    Mesa.objects.create(
        restaurante=restaurante,
        numero=numero_int,
        capacidad=capacidad_int,
        ubicacion=ubicacion,
        estado='libre',
        activa=True,
    )
    messages.success(request, f'Mesa #{numero_int} creada exitosamente.')
    return redirect('mesas:index')


@login_required(login_url='login')
@require_POST
def mesa_cambiar_estado(request, mesa_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para actualizar mesas.')
        return redirect('mesas:index')

    mesa = get_object_or_404(Mesa, pk=mesa_id, activa=True)
    accion = request.POST.get('accion')

    if accion == 'ocupar' and mesa.estado == 'libre':
        mesa.estado = 'ocupada'
        mesa.save(update_fields=['estado'])
        messages.success(request, f'Mesa #{mesa.numero} marcada como ocupada.')
    elif accion == 'liberar' and mesa.estado in ['ocupada', 'reservada']:
        mesa.estado = 'libre'
        mesa.save(update_fields=['estado'])
        messages.success(request, f'Mesa #{mesa.numero} marcada como libre.')
    else:
        messages.info(request, 'Acción no aplicada.')

    return redirect('mesas:index')


@login_required(login_url='login')
@require_POST
def mesa_eliminar(request, mesa_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para eliminar mesas.')
        return redirect('mesas:index')

    mesa = get_object_or_404(Mesa, pk=mesa_id, activa=True)
    numero_mesa = mesa.numero
    
    # Verificar si tiene pedidos activos
    pedidos_activos = mesa.pedidos.filter(
        archivado=False
    ).exclude(estado='cancelado').exists()
    
    if pedidos_activos:
        messages.error(request, f'No se puede eliminar la mesa #{numero_mesa}: tiene pedidos activos.')
        return redirect('mesas:index')
    
    # Desactivar en lugar de eliminar (soft delete)
    mesa.activa = False
    mesa.save(update_fields=['activa'])
    messages.success(request, f'Mesa #{numero_mesa} eliminada.')
    return redirect('mesas:index')

