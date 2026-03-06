from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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


@swagger_auto_schema(
    method='get',
    operation_description='Obtiene lista de mesas activas del restaurante en formato JSON',
    manual_parameters=[
        openapi.Parameter('estado', openapi.IN_QUERY, description="Filtrar por estado (libre, ocupada, reservada)", type=openapi.TYPE_STRING)
    ],
    responses={
        200: openapi.Response('Lista de mesas', examples={
            'application/json': {
                'mesas': [
                    {
                        'id': 1,
                        'numero': 1,
                        'capacidad': 4,
                        'estado': 'libre',
                        'estado_display': 'Libre'
                    }
                ]
            }
        })
    },
    tags=['Mesas API']
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def mesas_list_json(request):
    """Lista/crea mesas en formato JSON."""
    empleado = getattr(request.user, 'empleado', None)
    restaurante = getattr(empleado, 'restaurante', None) if empleado else None

    if request.method == 'POST':
        numero = request.data.get('numero')
        if not numero:
            return Response({'error': 'numero es obligatorio.'}, status=400)

        dup_qs = Mesa.objects.filter(numero=numero)
        if restaurante is not None:
            dup_qs = dup_qs.filter(restaurante=restaurante)

        existente = dup_qs.first()
        if existente:
            if not existente.activa:
                existente.capacidad = request.data.get('capacidad', existente.capacidad)
                existente.estado = request.data.get('estado', 'libre')
                existente.ubicacion = request.data.get('ubicacion', existente.ubicacion or '')
                existente.activa = True
                existente.save(update_fields=['capacidad', 'estado', 'ubicacion', 'activa'])
                mesa = existente
            else:
                return Response({'error': f'La mesa #{numero} ya existe para este restaurante.'}, status=400)
        else:
            try:
                mesa = Mesa.objects.create(
                    restaurante=restaurante,
                    numero=numero,
                    capacidad=request.data.get('capacidad', 4),
                    estado=request.data.get('estado', 'libre'),
                    ubicacion=request.data.get('ubicacion', ''),
                    activa=bool(request.data.get('activa', True)),
                )
            except IntegrityError:
                return Response({'error': f'La mesa #{numero} ya existe para este restaurante.'}, status=400)

        return Response({
            'mesa': {
                'id': mesa.id,
                'numero': mesa.numero,
                'capacidad': mesa.capacidad,
                'estado': mesa.estado,
                'estado_display': mesa.get_estado_display(),
            }
        }, status=201)

    estado = request.GET.get('estado')

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

    return Response({'mesas': mesas_data})


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def mesa_detail_json(request, mesa_id):
    empleado = getattr(request.user, 'empleado', None)
    restaurante = getattr(empleado, 'restaurante', None) if empleado else None
    mesa = get_object_or_404(Mesa, pk=mesa_id)
    if restaurante and not request.user.is_superuser and mesa.restaurante_id != getattr(restaurante, 'id', None):
        return Response({'error': 'No autorizado.'}, status=403)

    if request.method == 'DELETE':
        mesa.delete()
        return Response(status=204)

    for field in ['numero', 'capacidad', 'estado', 'ubicacion']:
        if field in request.data:
            setattr(mesa, field, request.data.get(field))
    if 'activa' in request.data:
        mesa.activa = bool(request.data.get('activa'))
    try:
        mesa.save()
    except IntegrityError:
        return Response({'error': f'La mesa #{mesa.numero} ya existe para este restaurante.'}, status=400)
    return Response({
        'mesa': {
            'id': mesa.id,
            'numero': mesa.numero,
            'capacidad': mesa.capacidad,
            'estado': mesa.estado,
            'estado_display': mesa.get_estado_display(),
        }
    })


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

    qs = Mesa.objects.filter(numero=numero_int)
    if restaurante is not None:
        qs = qs.filter(restaurante=restaurante)

    existente = qs.first()
    if existente:
        if existente.activa:
            messages.error(request, f'La mesa #{numero_int} ya existe para este restaurante.')
            return redirect('mesas:index')

        # Si la mesa existía inactiva, la reactivamos para no romper la restricción única.
        existente.capacidad = capacidad_int
        existente.ubicacion = ubicacion
        existente.estado = 'libre'
        existente.activa = True
        existente.save(update_fields=['capacidad', 'ubicacion', 'estado', 'activa'])
        messages.success(request, f'Mesa #{numero_int} reactivada exitosamente.')
        return redirect('mesas:index')

    try:
        Mesa.objects.create(
            restaurante=restaurante,
            numero=numero_int,
            capacidad=capacidad_int,
            ubicacion=ubicacion,
            estado='libre',
            activa=True,
        )
    except IntegrityError:
        messages.error(request, f'La mesa #{numero_int} ya existe para este restaurante.')
        return redirect('mesas:index')

    messages.success(request, f'Mesa #{numero_int} creada exitosamente.')
    return redirect('mesas:index')


@login_required(login_url='login')
@require_POST
def mesa_cambiar_estado(request, mesa_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para actualizar mesas.')
        return redirect('mesas:index')

    if mesa_id <= 0:
        messages.error(request, 'Mesa inválida.')
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

    if mesa_id <= 0:
        messages.error(request, 'Mesa inválida.')
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

