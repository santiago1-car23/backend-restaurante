from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from apps.core.permisos import requiere_permiso
from .models import Producto, Categoria, MenuDiario
from .forms import ProductoForm, CategoriaForm


def _restaurante_de_usuario(user):
    empleado = getattr(user, 'empleado', None)
    return getattr(empleado, 'restaurante', None) if empleado else None


@login_required(login_url='login')
def categoria_crear(request):
    """Crear una categoría de menú asociada al restaurante del usuario."""
    if not request.user.is_staff:
        return redirect('menu:index')

    restaurante = _restaurante_de_usuario(request.user)

    # Si el usuario no tiene restaurante asociado no permitimos crear categorías
    if restaurante is None and not request.user.is_superuser:
        return redirect('menu:index')

    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.restaurante = restaurante
            categoria.save()
            return redirect('menu:categoria_lista')
    else:
        form = CategoriaForm()

    return render(request, 'menu/categoria_form.html', {
        'form': form,
        'titulo': 'Nueva categoría de menú',
    })


@login_required(login_url='login')
def categoria_list(request):
    """Listado de categorías del restaurante del usuario."""
    if not request.user.is_staff:
        return redirect('menu:index')

    restaurante = _restaurante_de_usuario(request.user)

    # Si el usuario no tiene restaurante asociado no mostramos categorías
    if not restaurante:
        return redirect('menu:index')

    categorias = Categoria.objects.filter(restaurante=restaurante).order_by('nombre')

    return render(request, 'menu/categoria_list.html', {
        'categorias': categorias,
        'active': 'menu',
    })


@login_required(login_url='login')
def categoria_editar(request, categoria_id):
    """Editar una categoría, limitada al restaurante del usuario."""
    if not request.user.is_staff:
        return redirect('menu:index')

    restaurante = _restaurante_de_usuario(request.user)

    if not restaurante:
        return redirect('menu:index')

    categoria = get_object_or_404(Categoria, pk=categoria_id, restaurante=restaurante)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('menu:categoria_lista')
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'menu/categoria_form.html', {
        'form': form,
        'titulo': f'Editar categoría: {categoria.nombre}',
    })


@login_required(login_url='login')
def categoria_eliminar(request, categoria_id):
    """Eliminar una categoría del menú para el restaurante del usuario."""
    if not request.user.is_staff:
        return redirect('menu:index')

    restaurante = _restaurante_de_usuario(request.user)

    if not restaurante:
        return redirect('menu:index')

    categoria = get_object_or_404(Categoria, pk=categoria_id, restaurante=restaurante)

    if request.method == 'POST':
        categoria.delete()
        return redirect('menu:categoria_lista')

    return render(request, 'menu/categoria_confirm_delete.html', {
        'categoria': categoria,
    })


@login_required(login_url='login')
def menu_list(request):
    categoria_id = request.GET.get('categoria')
    query = (request.GET.get('q') or '').strip()

    restaurante = _restaurante_de_usuario(request.user)

    productos = Producto.objects.filter(disponible=True).select_related('categoria')
    if restaurante:
        productos = productos.filter(categoria__restaurante=restaurante)

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )
    
    categorias = Categoria.objects.filter(activo=True)
    if restaurante:
        categorias = categorias.filter(restaurante=restaurante)

    # Asegurar categorías fijas SOLO si el restaurante aún no tiene ninguna
    categorias_fijas = ['Snacks', 'Postres', 'Platos', 'Bebidas']

    if not categorias.exists():
        for nombre_cat in categorias_fijas:
            Categoria.objects.create(
                restaurante=restaurante,
                nombre=nombre_cat,
                activo=True,
            )

        # Recargar categorías para incluir las recién creadas
        categorias = Categoria.objects.filter(activo=True)
        if restaurante:
            categorias = categorias.filter(restaurante=restaurante)

    # Obtener ID de Snacks para el template
    snacks_categoria = categorias.filter(nombre__iexact='snacks').first()
    snacks_categoria_id = snacks_categoria.id if snacks_categoria else None
    
    context = {
        'active': 'menu',
        'productos': productos,
        'categorias': categorias,
        'snacks_categoria_id': snacks_categoria_id,
        'categoria_id': categoria_id,
        'query': query,
    }
    return render(request, 'menu/menu_list.html', context)


@login_required(login_url='login')
def producto_crear(request):
    if not request.user.is_staff:
        return redirect('menu:index')

    restaurante = _restaurante_de_usuario(request.user)

    if request.method == 'POST':
        # Pasamos el restaurante al formulario para que pueda leer/escribir el stock
        form = ProductoForm(request.POST, request.FILES, restaurante=restaurante)

        # Limitar categorías al restaurante del usuario para evitar ver categorías de otros restaurantes
        if restaurante:
            form.fields['categoria'].queryset = Categoria.objects.filter(activo=True, restaurante=restaurante)

        if form.is_valid():
            producto = form.save()

            # Forzar que la categoría del producto pertenezca al restaurante del usuario
            if restaurante and producto.categoria and producto.categoria.restaurante is None:
                producto.categoria.restaurante = restaurante
                producto.categoria.save(update_fields=['restaurante'])

            # Conectar con inventario: crear/actualizar ingrediente con el stock inicial
            stock = form.cleaned_data.get('stock_inicial')
            if stock is not None:
                try:
                    from apps.inventario.models import Ingrediente

                    ingrediente, creado = Ingrediente.objects.get_or_create(
                        nombre=producto.nombre,
                        restaurante=restaurante,
                        defaults={
                            'unidad': 'unidad',
                            'cantidad_actual': stock,
                            'cantidad_minima': 0,
                            'costo_unitario': producto.precio,
                        },
                    )
                    if not creado:
                        ingrediente.cantidad_actual = stock
                        ingrediente.costo_unitario = producto.precio
                        ingrediente.save()
                except Exception:
                    # Si algo falla con inventario, no bloqueamos la creación del producto
                    pass
            return redirect('menu:index')
    else:
        # También en GET pasamos el restaurante para precargar correctamente el stock inicial
        form = ProductoForm(restaurante=restaurante)

        if restaurante:
            form.fields['categoria'].queryset = Categoria.objects.filter(activo=True, restaurante=restaurante)

    return render(request, 'menu/producto_form.html', {
        'form': form,
        'titulo': 'Nuevo producto',
    })


@login_required(login_url='login')
def producto_editar(request, producto_id):
    if not request.user.is_staff:
        return redirect('menu:index')

    restaurante = _restaurante_de_usuario(request.user)

    if restaurante and not request.user.is_superuser:
        producto = get_object_or_404(Producto, pk=producto_id, categoria__restaurante=restaurante)
    else:
        producto = get_object_or_404(Producto, pk=producto_id)

    if request.method == 'POST':
        # Pasamos el restaurante para que el formulario cargue y actualice el stock del
        # ingrediente correspondiente a este restaurante
        form = ProductoForm(request.POST, request.FILES, instance=producto, restaurante=restaurante)

        if restaurante:
            form.fields['categoria'].queryset = Categoria.objects.filter(activo=True, restaurante=restaurante)

        if form.is_valid():
            producto = form.save()

            # Actualizar también el stock en inventario si se especifica
            stock = form.cleaned_data.get('stock_inicial')
            if stock is not None:
                try:
                    from apps.inventario.models import Ingrediente

                    ingrediente, creado = Ingrediente.objects.get_or_create(
                        nombre=producto.nombre,
                        restaurante=restaurante,
                        defaults={
                            'unidad': 'unidad',
                            'cantidad_actual': stock,
                            'cantidad_minima': 0,
                            'costo_unitario': producto.precio,
                        },
                    )
                    if not creado:
                        ingrediente.cantidad_actual = stock
                        ingrediente.costo_unitario = producto.precio
                        ingrediente.save()
                except Exception:
                    pass
            return redirect('menu:index')
    else:
        # En edición GET también pasamos el restaurante para precargar stock desde inventario
        form = ProductoForm(instance=producto, restaurante=restaurante)

        if restaurante:
            form.fields['categoria'].queryset = Categoria.objects.filter(activo=True, restaurante=restaurante)

    return render(request, 'menu/producto_form.html', {
        'form': form,
        'titulo': f'Editar producto: {producto.nombre}',
    })


@login_required(login_url='login')
def producto_eliminar(request, producto_id):
    if not request.user.is_authenticated:
        return redirect('login')

    # Solo personal autorizado (staff o admin de restaurante)
    from apps.usuarios.models import Empleado

    es_staff = request.user.is_staff or request.user.is_superuser
    empleado = getattr(request.user, 'empleado', None)
    rol = getattr(empleado, 'rol', None) if empleado else None
    nombre_rol = getattr(rol, 'nombre', None)
    puede_borrar = es_staff or nombre_rol == 'admin'

    if not puede_borrar:
        return redirect('menu:index')

    restaurante = getattr(empleado, 'restaurante', None) if empleado else None

    if restaurante and not request.user.is_superuser:
        producto = get_object_or_404(Producto, pk=producto_id, categoria__restaurante=restaurante)
    else:
        producto = get_object_or_404(Producto, pk=producto_id)

    if request.method == 'POST':
        # Guardar datos antes de borrar el producto para poder eliminar el ingrediente asociado
        nombre_prod = producto.nombre
        restaurante_prod = producto.categoria.restaurante if producto.categoria else None

        producto.delete()

        # También intentar eliminar el ingrediente de inventario correspondiente a este producto
        try:
            from apps.inventario.models import Ingrediente

            if restaurante_prod is not None:
                Ingrediente.objects.filter(
                    nombre=nombre_prod,
                    restaurante=restaurante_prod,
                ).delete()
            else:
                Ingrediente.objects.filter(
                    nombre=nombre_prod,
                    restaurante__isnull=True,
                ).delete()
        except Exception:
            # Si algo falla con inventario, no bloqueamos la eliminación del producto
            pass
        return redirect('menu:index')

    return render(request, 'menu/producto_confirm_delete.html', {
        'producto': producto,
    })


@login_required(login_url='login')
def menu_corriente(request):
    """Vista para ver y editar el menú del día."""
    # Obtener fecha desde GET/POST o usar hoy
    fecha_str = request.GET.get('fecha') or request.POST.get('fecha')
    if fecha_str:
        try:
            fecha_sel = date.fromisoformat(fecha_str)
        except ValueError:
            fecha_sel = date.today()
    else:
        fecha_sel = date.today()

    restaurante = _restaurante_de_usuario(request.user)
    menu_obj, _ = MenuDiario.objects.get_or_create(fecha=fecha_sel, restaurante=restaurante)

    if request.method == 'POST' and request.user.is_staff:
        menu_obj.sopa = request.POST.get('sopa', '').strip()
        menu_obj.principios = request.POST.get('principio', '').strip()
        menu_obj.proteinas = request.POST.get('proteina', '').strip()
        menu_obj.acompanante = request.POST.get('acompanante', '').strip()
        menu_obj.limonada = request.POST.get('limonada', '').strip()
        precio_sopa_str = request.POST.get('precio_sopa', '').strip()
        precio_bandeja_str = request.POST.get('precio_bandeja', '').strip()
        precio_completo_str = request.POST.get('precio_completo', '').strip()

        try:
            if precio_sopa_str:
                menu_obj.precio_sopa = Decimal(precio_sopa_str)
        except Exception:
            pass
        try:
            if precio_bandeja_str:
                menu_obj.precio_bandeja = Decimal(precio_bandeja_str)
        except Exception:
            pass
        try:
            if precio_completo_str:
                menu_obj.precio_completo = Decimal(precio_completo_str)
        except Exception:
            pass
        menu_obj.save()

        return redirect(f"{request.path}?fecha={fecha_sel.isoformat()}")

    def _split_lista(valor: str):
        return [v.strip() for v in valor.split(',') if v.strip()] if valor else []

    menu_ns = SimpleNamespace(
        sopa=menu_obj.sopa,
        principio=_split_lista(menu_obj.principios),
        proteina=_split_lista(menu_obj.proteinas),
        acompanante=menu_obj.acompanante,
        limonada=menu_obj.limonada,
        precio_sopa=menu_obj.precio_sopa,
        precio_bandeja=menu_obj.precio_bandeja,
        precio_completo=menu_obj.precio_completo,
    )

    categorias = Categoria.objects.filter(activo=True)

    context = {
        'menu': menu_ns,
        'fecha': fecha_sel.isoformat(),
        'categorias': categorias,  # por si luego quieres ligarlo a productos
    }
    return render(request, 'menu/menu_corriente.html', context)


@login_required(login_url='login')
def menu_desayuno(request):
    """Vista para ver y editar el menú de desayuno del día.

    Usa los campos desayuno_* de MenuDiario para configurar un desayuno tipo "corriente".
    """
    fecha_str = request.GET.get('fecha') or request.POST.get('fecha')
    if fecha_str:
        try:
            fecha_sel = date.fromisoformat(fecha_str)
        except ValueError:
            fecha_sel = date.today()
    else:
        fecha_sel = date.today()

    restaurante = _restaurante_de_usuario(request.user)
    menu_obj, _ = MenuDiario.objects.get_or_create(fecha=fecha_sel, restaurante=restaurante)

    if request.method == 'POST' and request.user.is_staff:
        menu_obj.desayuno_principales = request.POST.get('desayuno_principales', '').strip()
        menu_obj.desayuno_bebidas = request.POST.get('desayuno_bebidas', '').strip()
        menu_obj.desayuno_acompanante = request.POST.get('desayuno_acompanante', '').strip()
        menu_obj.caldos = request.POST.get('caldos', '').strip()
        precio_desayuno_str = request.POST.get('precio_desayuno', '').strip()

        try:
            if precio_desayuno_str:
                menu_obj.precio_desayuno = Decimal(precio_desayuno_str)
        except Exception:
            pass

        menu_obj.save()

        return redirect(f"{request.path}?fecha={fecha_sel.isoformat()}")

    def _split_lista(valor: str):
        return [v.strip() for v in valor.split(',') if v.strip()] if valor else []

    menu_ns = SimpleNamespace(
        principales=_split_lista(menu_obj.desayuno_principales),
        bebidas=_split_lista(menu_obj.desayuno_bebidas),
        caldos=_split_lista(menu_obj.caldos),
        acompanante=menu_obj.desayuno_acompanante,
        precio_desayuno=menu_obj.precio_desayuno,
        # Para mostrar texto original en textarea
        principales_raw=menu_obj.desayuno_principales,
        bebidas_raw=menu_obj.desayuno_bebidas,
        caldos_raw=menu_obj.caldos,
    )

    context = {
        'menu': menu_ns,
        'fecha': fecha_sel.isoformat(),
    }
    return render(request, 'menu/menu_desayuno.html', context)

