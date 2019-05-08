# -*- coding: utf-8 -*-
from django import template
from django.contrib.auth.models import Group
from django.forms.forms import BoundField
from ..views import AsteriskAmi
from bs4 import BeautifulSoup

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    return True if group_name in user.ldap_user.group_names else False


@register.filter(name='agent_parse')
def agent_parse(queue_member):
    import re
    return re.search('(\d+)', queue_member).group(0)

@register.filter(name='getdict_item')
def get2_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='agent_phone')
#@TODO: not working, not using, agent not digit only
def agent_phone(agent):
    print agent
    return AsteriskAmi().get_response(dict(Action='DBGet', Family='agent_sip', Key=agent))


