#!/usr/bin/env python
# encoding: utf-8

from django.conf import settings


def settings_values(request):
    """
    Context processor, which sends setting values to templates.
    """
    return {'settings': settings}
