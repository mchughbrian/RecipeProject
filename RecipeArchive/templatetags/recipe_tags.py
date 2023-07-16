from django import template

register = template.Library()

@register.filter
def starts_with(value, arg):
    """Checks if value starts with provided arg."""
    return str(value).startswith(str(arg))
