from django import template

register = template.Library()


def _formatear_pesos(valor):
    try:
        # Convertir a entero de pesos (asumiendo que viene como Decimal o número)
        entero = int(round(float(valor)))
    except (TypeError, ValueError):
        return "0"

    # Usar separador de miles con coma y luego cambiar a punto
    return f"{entero:,}".replace(",", ".")


@register.filter(name="pesos")
def pesos(value):
    """Formatea un número como pesos colombianos: 2000 -> 2.000"""
    return _formatear_pesos(value)
