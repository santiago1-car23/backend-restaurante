from decimal import Decimal, InvalidOperation


def formatear_pesos_colombianos(valor) -> str:
    try:
        numero = Decimal(str(valor or 0))
    except (InvalidOperation, ValueError, TypeError):
        numero = Decimal('0')

    numero = numero.quantize(Decimal('0.01'))
    entero = int(numero)
    decimales = int((numero - Decimal(entero)) * 100)
    entero_formateado = f"{entero:,}".replace(",", ".")

    if decimales:
        return f"${entero_formateado},{decimales:02d}"
    return f"${entero_formateado}"
