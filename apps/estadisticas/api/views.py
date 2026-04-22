from datetime import date, datetime

from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.caja.models import Factura, CajaSesion


def _restaurante_de_usuario(user):
    empleado = getattr(user, 'empleado', None)
    return getattr(empleado, 'restaurante', None) if empleado else None


class ResumenMensualView(APIView):
    """Endpoint REST para el resumen mensual de estadísticas.

    Replica la lógica de apps.estadisticas.views.resumen_mensual pero devuelve JSON.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        restaurante = _restaurante_de_usuario(request.user)

        hoy = date.today()
        year = hoy.year
        month = hoy.month

        year_param = request.query_params.get('year')
        if year_param:
            try:
                year = int(year_param)
            except (TypeError, ValueError):
                pass

        month_param = request.query_params.get('month')
        if month_param:
            try:
                month = int(month_param)
            except (TypeError, ValueError):
                pass

        period = request.query_params.get('period')  # YYYY-MM
        if period:
            try:
                period_dt = datetime.strptime(period, '%Y-%m')
                year = period_dt.year
                month = period_dt.month
            except ValueError:
                pass

        facturas_qs = Factura.objects.filter(fecha__year=year, fecha__month=month)
        if restaurante:
            facturas_qs = facturas_qs.filter(pedido__restaurante=restaurante)

        total_mes = facturas_qs.aggregate(total=Sum('total'))['total'] or 0
        total_facturas = facturas_qs.count()

        sesiones_cerradas = CajaSesion.objects.filter(
            estado='cerrada',
            fecha_cierre__year=year,
            fecha_cierre__isnull=False,
        )
        if restaurante:
            sesiones_cerradas = sesiones_cerradas.filter(restaurante=restaurante)

        meses_labels = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
        ]
        meses_totales = [0.0] * 12

        for sesion in sesiones_cerradas:
            if sesion.fecha_cierre:
                idx = sesion.fecha_cierre.month - 1
                meses_totales[idx] += float(sesion.resultado_neto or 0)

        period_value = f"{year:04d}-{month:02d}"

        data = {
            'hoy': hoy.isoformat(),
            'year': year,
            'month': month,
            'period_value': period_value,
            'total_mes': float(total_mes),
            'total_facturas': total_facturas,
            'labels_meses': meses_labels,
            'data_meses': meses_totales,
        }
        return Response(data)
