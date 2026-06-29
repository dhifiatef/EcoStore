from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (TypeError, ValueError):
        return value

@register.filter
def percentage(value, total):
    try:
        if float(total) == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (TypeError, ValueError):
        return 0

@register.simple_tag
def active_class(request_path, url_name, css_class='active'):
    if url_name in request_path:
        return css_class
    return ''

@register.filter
def currency(value):
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return value

@register.filter
def status_color(status):
    colors = {
        'pending':    'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
        'processing': 'text-blue-400 bg-blue-400/10 border-blue-400/20',
        'shipped':    'text-purple-400 bg-purple-400/10 border-purple-400/20',
        'delivered':  'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
        'cancelled':  'text-red-400 bg-red-400/10 border-red-400/20',
    }
    return colors.get(status, 'text-zinc-400 bg-zinc-400/10 border-zinc-400/20')

@register.filter
def stock_color(stock):
    if stock == 0:
        return 'text-red-400'
    if stock < 10:
        return 'text-yellow-400'
    return 'text-emerald-400'
