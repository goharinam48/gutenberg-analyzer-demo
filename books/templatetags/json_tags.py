from django import template
import json

register = template.Library()

@register.filter
def get_item(value, key):
    try:
        data = json.loads(value) if isinstance(value, str) else value
        return data.get(key, '')
    except (json.JSONDecodeError, AttributeError):
        return ''