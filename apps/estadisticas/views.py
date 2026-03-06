from datetime import date, datetime
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from apps.caja.models import Factura, CajaSesion


def _restaurante_de_usuario(user):
    """Obtiene el restaurante asociado al empleado del usuario, si existe."""
    empleado = getattr(user, 'empleado', None)
    return getattr(empleado, 'restaurante', None) if empleado else None


@login_required(login_url='login')
def resumen_mensual(request):
    """Resumen mensual del negocio con estadísticas básicas."""
    restaurante = _restaurante_de_usuario(request.user)

    hoy = date.today()
    # Valores por defecto: mes y año actuales
    year = hoy.year
    month = hoy.month

    # Permitir año y mes por separado (compatibilidad)
    year_param = request.GET.get('year')
    if year_param:
        try:
            year = int(year_param)
        except (TypeError, ValueError):
            pass

    month_param = request.GET.get('month')
    if month_param:
        try:
            month = int(month_param)
        except (TypeError, ValueError):
            pass

    # Nuevo: selector de mes con calendario (input type="month")
    period = request.GET.get('period')  # formato esperado: YYYY-MM
    if period:
        try:
            period_dt = datetime.strptime(period, '%Y-%m')
            year = period_dt.year
            month = period_dt.month
        except ValueError:
            # Si viene mal formateado, se ignora y se mantienen year/month actuales
            pass

    facturas_qs = Factura.objects.filter(fecha__year=year, fecha__month=month)
    if restaurante:
        facturas_qs = facturas_qs.filter(pedido__restaurante=restaurante)

    total_mes = facturas_qs.aggregate(total=Sum('total'))['total'] or 0
    total_facturas = facturas_qs.count()

    # Resumen anual por cierres de caja (resultado neto por mes)
    # Usa el mismo año seleccionado en el filtro
    sesiones_cerradas = CajaSesion.objects.filter(
        estado='cerrada',
        fecha_cierre__year=year,
        fecha_cierre__isnull=False,
    )
    if restaurante:
        sesiones_cerradas = sesiones_cerradas.filter(restaurante=restaurante)

    # Inicializamos 12 meses en cero
    meses_labels = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
    ]
    meses_totales = [0.0] * 12

    for sesion in sesiones_cerradas:
        if sesion.fecha_cierre:
            idx = sesion.fecha_cierre.month - 1
            # Usamos el resultado_neto de la sesión como "cómo fue el mes"
            meses_totales[idx] += float(sesion.resultado_neto or 0)

    period_value = f"{year:04d}-{month:02d}"

    contexto = {
        'hoy': hoy,
        'year': year,
        'month': month,
        'period_value': period_value,
        'total_mes': total_mes,
        'total_facturas': total_facturas,
        'labels_meses_json': json.dumps(meses_labels),
        'data_meses_json': json.dumps(meses_totales),
    }
    return render(request, 'estadisticas/resumen_mensual.html', contexto)
