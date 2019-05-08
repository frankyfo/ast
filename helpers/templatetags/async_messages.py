#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template import Library
from offline_messages.models import OfflineMessage

register = Library()


def unread_messages(user):
    return OfflineMessage.objects.filter(read=False,user=user).count()


register.filter('unread_messages',unread_messages)

