from django import template

register = template.Library()

@register.filter(name='format_cop')
def format_cop(value):
    """Formatea un valor numérico como precio en COP"""
    try:
        return f"${float(value):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "$0"

@register.filter(name='selectattr')
def selectattr(lst, attr_value):
    """Filtra una lista por un atributo específico"""
    if not lst:
        return []
    attr, value = attr_value.split(',')
    return [item for item in lst if getattr(item, attr.strip(), None) == value.strip()]
