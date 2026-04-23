from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Ingrediente, MovimientoInventario
from apps.menu.models import Producto
from .forms import IngredienteForm, MovimientoInventarioForm


def _puede_gestionar_inventario(user):
    """Devuelve True si el usuario puede crear/editar/eliminar inventario."""
    if not user.is_authenticated:
        return False

    if user.is_staff or user.is_superuser:
        return True

    empleado = getattr(user, 'empleado', None)
    rol = getattr(empleado, 'rol', None) if empleado else None
    nombre_rol = getattr(rol, 'nombre', None)
    return nombre_rol == 'admin'


@login_required(login_url='login')
def inventario_list(request):
    """Listado de ingredientes con filtros básicos y alertas de stock."""
    empleado = getattr(request.user, 'empleado', None)
    restaurante = getattr(empleado, 'restaurante', None) if empleado else None

    # Sincronizar productos del menú como ingredientes si no existen
    # Solo para el restaurante del empleado; evitar mezclar restaurantes.
    if restaurante:
        productos_menu = Producto.objects.filter(categoria__restaurante=restaurante)

        for producto in productos_menu:
            qs_ing = Ingrediente.objects.filter(nombre=producto.nombre, restaurante=restaurante)
            if not qs_ing.exists():
                Ingrediente.objects.create(
                    restaurante=restaurante,
                    nombre=producto.nombre,
                    unidad='unidad',
                    cantidad_actual=0,
                    cantidad_minima=0,
                    costo_unitario=producto.precio,
                )

    query = (request.GET.get('q') or '').strip()
    solo_bajo_stock = request.GET.get('criticos') == '1'

    if restaurante:
        ingredientes = Ingrediente.objects.filter(restaurante=restaurante)
    else:
        # Si no tiene restaurante y no es superusuario, no mostrar inventario global
        if request.user.is_superuser:
            ingredientes = Ingrediente.objects.all()
        else:
            ingredientes = Ingrediente.objects.none()

    if query:
        ingredientes = ingredientes.filter(
            Q(nombre__icontains=query)
        )

    if solo_bajo_stock:
        ingredientes = [i for i in ingredientes if i.alerta_stock()]

    total = ingredientes.count()
    criticos = sum(1 for i in ingredientes if i.alerta_stock())

    context = {
        'active': 'inventario',
        'ingredientes': ingredientes,
        'query': query,
        'solo_bajo_stock': solo_bajo_stock,
        'total_ingredientes': total,
        'ingredientes_criticos': criticos,
        'puede_gestionar_inventario': _puede_gestionar_inventario(request.user),
    }
    return render(request, 'inventario/inventario_list.html', context)


@login_required(login_url='login')
def ingrediente_nuevo(request):
    if not _puede_gestionar_inventario(request.user):
        messages.error(request, 'No tienes permiso para gestionar el inventario.')
        return redirect('inventario:index')

    empleado = getattr(request.user, 'empleado', None)
    restaurante = getattr(empleado, 'restaurante', None) if empleado else None

    if request.method == 'POST':
        form = IngredienteForm(request.POST)
        if form.is_valid():
            ingrediente = form.save(commit=False)
            ingrediente.restaurante = restaurante
            ingrediente.save()
            messages.success(request, 'Ingrediente creado correctamente.')
            return redirect('inventario:index')
    else:
        form = IngredienteForm()

    return render(request, 'inventario/ingrediente_form.html', {
        'form': form,
        'titulo': 'Nuevo ingrediente',
    })


@login_required(login_url='login')
def ingrediente_editar(request, ingrediente_id):
    if not _puede_gestionar_inventario(request.user):
        messages.error(request, 'No tienes permiso para gestionar el inventario.')
        return redirect('inventario:index')

    empleado = getattr(request.user, 'empleado', None)
    restaurante = getattr(empleado, 'restaurante', None) if empleado else None

    if restaurante and not request.user.is_superuser:
        ingrediente = get_object_or_404(Ingrediente, pk=ingrediente_id, restaurante=restaurante)
    else:
        ingrediente = get_object_or_404(Ingrediente, pk=ingrediente_id)

    if request.method == 'POST':
        form = IngredienteForm(request.POST, instance=ingrediente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingrediente actualizado correctamente.')
            return redirect('inventario:index')
    else:
        form = IngredienteForm(instance=ingrediente)

    return render(request, 'inventario/ingrediente_form.html', {
        'form': form,
        'titulo': f'Editar ingrediente: {ingrediente.nombre}',
    })


@login_required(login_url='login')
def ingrediente_eliminar(request, ingrediente_id):
    if not _puede_gestionar_inventario(request.user):
        messages.error(request, 'No tienes permiso para gestionar el inventario.')
        return redirect('inventario:index')

    empleado = getattr(request.user, 'empleado', None)
    restaurante = getattr(empleado, 'restaurante', None) if empleado else None

    if restaurante and not request.user.is_superuser:
        ingrediente = get_object_or_404(Ingrediente, pk=ingrediente_id, restaurante=restaurante)
    else:
        ingrediente = get_object_or_404(Ingrediente, pk=ingrediente_id)

    if request.method == 'POST':
        # Guardar datos antes de borrar para poder eliminar productos asociados
        nombre_ing = ingrediente.nombre
        restaurante_ing = ingrediente.restaurante

        # Eliminar ingrediente del inventario
        ingrediente.delete()

        # También eliminar productos de menú que usen este ingrediente (mismo nombre y restaurante)
        try:
            if restaurante_ing is not None:
                Producto.objects.filter(
                    nombre=nombre_ing,
                    categoria__restaurante=restaurante_ing,
                ).delete()
            else:
                Producto.objects.filter(
                    nombre=nombre_ing,
                    categoria__restaurante__isnull=True,
                ).delete()
        except Exception:
            # Si algo falla al borrar productos, no bloqueamos la eliminación del ingrediente
            pass

        messages.success(request, 'Ingrediente (y productos asociados) eliminado correctamente.')
        return redirect('inventario:index')

    return render(request, 'inventario/ingrediente_confirm_delete.html', {
        'ingrediente': ingrediente,
    })


@login_required(login_url='login')
def movimientos_list(request):
    """Lista de movimientos de inventario con filtros simples."""
    empleado = getattr(request.user, 'empleado', None)
    restaurante = getattr(empleado, 'restaurante', None) if empleado else None
    ingrediente_id = request.GET.get('ingrediente')
    tipo = request.GET.get('tipo')

    movimientos = MovimientoInventario.objects.select_related('ingrediente', 'usuario')

    if restaurante and not request.user.is_superuser:
        movimientos = movimientos.filter(ingrediente__restaurante=restaurante)
    elif not restaurante and not request.user.is_superuser:
        # Usuario sin restaurante asignado: no debe ver movimientos de otros restaurantes
        movimientos = movimientos.none()

    if ingrediente_id:
        movimientos = movimientos.filter(ingrediente_id=ingrediente_id)
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)

    if restaurante:
        ingredientes_qs = Ingrediente.objects.filter(restaurante=restaurante)
    else:
        ingredientes_qs = Ingrediente.objects.all() if request.user.is_superuser else Ingrediente.objects.none()

    context = {
        'movimientos': movimientos,
        'ingredientes': ingredientes_qs,
        'ingrediente_id': ingrediente_id,
        'tipo': tipo,
    }
    return render(request, 'inventario/movimientos_list.html', context)


@login_required(login_url='login')
def movimiento_nuevo(request):
    if not _puede_gestionar_inventario(request.user):
        messages.error(request, 'No tienes permiso para registrar movimientos de inventario.')
        return redirect('inventario:movimientos')

    empleado = getattr(request.user, 'empleado', None)
    restaurante = getattr(empleado, 'restaurante', None) if empleado else None

    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            movimiento.save()
            messages.success(request, 'Movimiento registrado correctamente.')
            return redirect('inventario:movimientos')
    else:
        form = MovimientoInventarioForm()

    # Limitar ingredientes al restaurante del usuario
    if restaurante:
        form.fields['ingrediente'].queryset = Ingrediente.objects.filter(restaurante=restaurante)
    else:
        form.fields['ingrediente'].queryset = Ingrediente.objects.all() if request.user.is_superuser else Ingrediente.objects.none()

    return render(request, 'inventario/movimiento_form.html', {
        'form': form,
        'titulo': 'Nuevo movimiento de inventario',
    })

