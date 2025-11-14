from django import template
from django.utils import timezone
import pytz
from scoreboard.models import CTFConfig

register = template.Library()

@register.filter
def to_ctf_timezone(value):
    """Convierte una fecha a la zona horaria configurada en el CTF"""
    if not value:
        return value
    
    config = CTFConfig.get_config()
    try:
        tz = pytz.timezone(config.timezone)
        if timezone.is_aware(value):
            return value.astimezone(tz)
        else:
            return timezone.make_aware(value, timezone.utc).astimezone(tz)
    except:
        return value
