from django import template
from widget_tweaks.templatetags.widget_tweaks import add_class

register = template.Library()

@register.filter
def add_class_if(field, css_class):
    if field.errors:
        return add_class(field, css_class)
    return field
