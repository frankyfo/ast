# -*- coding: utf-8 -*-
from django import template
from django.contrib.auth.models import Group
from django.forms.forms import BoundField

register = template.Library()


@register.filter(name='linecut')
def linecut(value):
    if len(value) > 25:
        return value[:25] + '...'
    else:
        return value



@register.filter(name='has_group')
def has_group(user, group_name):
    return True if group_name in user.ldap_user.group_names else False


@register.filter(name='has_any_group')
def has_any_group(user, groups):
    groups = [g.strip() for g in groups.split(',')]
    return user.groups.filter(name__in=groups).exists()


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='map_state')
def map_state(state):
    states = {'open': 'Открыт', 'close': 'Закрыт', 'process': 'Комплект отправлен', 'prepare': 'Подготовить',
              'done': 'Настроен', 'terminated': 'Временно не работает'}
    return states[state]


@register.filter(name='css')
def css(field, css):
    return field.as_widget(attrs={"class": css})
