from django.core.serializers.json import DjangoJSONEncoder
import datetime
import decimal
from django.utils.timezone import is_aware
import inspect
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


class RuDateJSONEncoder(DjangoJSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.strftime('%d.%m.%Y')
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(DjangoJSONEncoder, self).default(o)


import os
import string


def random_password(length=10):
    chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
    password = ''
    for i in range(length):
        password += chars[ord(os.urandom(1)) % len(chars)]
    return password


def get_var_or_raise(param, where=settings):
    stack = inspect.stack()
    if isinstance(where, dict) and param in where:
        return where.get(param)
    if not hasattr(where, param):
        raise ImproperlyConfigured("No variable \"%s\" defined! Cannot perform task \"%s\"" %
                                   (param, stack[1][3]))
    return getattr(where, param)


def to_bool(value, default=False):
    """
    Converts to bool, if not successful - returns default
    :param value: value to convert
    :param default: default value if no conversion can be possible
    :return:
    """
    try:
        return bool(value)
    except (TypeError, ValueError):
        return default
