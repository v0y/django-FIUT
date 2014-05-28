# encoding: utf-8

import datetime
from itertools import chain
import types

from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.defaultfilters import slugify as django_slugify
from django.template.loader import render_to_string
from django.utils import timezone

try:
    # fuck you, python 2.7
    str = unicode
except NameError:
    pass


def simple_send_email(
        subject, message, recipients, html_message=None,
        subject_data=None, message_data=None, html_message_data=None,
        from_email=None, attachments=None, auth_user=None, auth_password=None,
        connection=None, headers=None):
    """
    Send email using default or given email backend

    :param subject: String, email subject template path (*.txt)
                    or subject string
    :param message: String, email content template path (*.txt)
                    or plain text message
    :param recipients: String or list of strings, each an email address
    :param html_message: String, email content template path
                         (*.html, *.html) or html message
    :param subject_data: dict for extra data for subject template
    :param message_data: dict for extra data for message template
    :param html_message_data: dict for extra data for html message
                              template
    :param from_email: sender email
    :param attachments: list, tuple, generator or dict of attachment
                        (attachements are values)
    :param auth_user: username for email backend
    :param auth_password: password for email backend
    :param connection: loaded email backend
    :param headers: email headers
    """

    headers = headers or {}
    from_email = from_email or settings.DEFAULT_FROM_EMAIL
    fail_silently = False if settings.DEBUG else True
    allowed_message_template_extensions = ('.txt',)
    allowed_html_message_template_extensions = ('.html', '.htm')
    allowed_subject_template_extensions = ('.txt',)

    subject_data = subject_data or {}
    message_data = message_data or {}

    connection = connection or get_connection(
        username=auth_user, password=auth_password,
        fail_silently=fail_silently)

    # parse subject template
    if subject.endswith(allowed_subject_template_extensions):
        subject_str = \
            render_to_string(subject, subject_data).replace('\n', ' ')
    else:
        subject_str = subject.replace('\n', ' ')

    # parse message template
    if message.endswith(allowed_message_template_extensions):
        message_str = render_to_string(message, message_data)
    else:
        message_str = message

    # check, if var recipients is list or string
    if not type(recipients) in [list, tuple]:
        recipients = [recipients]

    # create email message
    message = EmailMultiAlternatives(
        subject_str, message_str, from_email, recipients,
        connection=connection, headers=headers)

    # parse and attach html message template
    if html_message:
        if html_message.endswith(allowed_html_message_template_extensions):
            html_message_str = render_to_string(
                html_message, html_message_data)
        else:
            html_message_str = html_message
        message.attach_alternative(html_message_str, "text/html")

    # attach attachments
    if attachments:
        if type(attachments) is dict:
            try:
                attachments_iterable = attachments.itervalues()
            except AttributeError:
                attachments_iterable = attachments.values()
        elif type(attachments) in (tuple, list, types.GeneratorType):
            attachments_iterable = attachments
        else:
            raise TypeError(
                "Unhandled attachments type: %s" % type(attachments))

        attachments_iterable = chain.from_iterable(list(attachments_iterable))

        for attach in attachments_iterable:
            message.attach(str(attach), attach.read(), attach.content_type)

    return message.send()


def get_page_and_paginator(request, objects, per_page=10, few_visible=3):
    """
    Get page and paginator

    :param objects: queryset of objects to paginate
    :param per_page: int, number of objects per page
    :param few_visible: numbers visible on beginning and ending of
                        paginator, like: [1, 2, 3 ... 7, 8, 9]
    :return: paginator page and paginator
    :rtype: tuple
    """
    paginator = Paginator(objects, per_page)
    num_pages = paginator.num_pages
    page = request.GET.get('page')

    try:
        page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.page(num_pages)

    # set first and last visible pages ranges
    page.paginator.first_few = range(1, few_visible + 1)
    page.paginator.first_few_border = few_visible + 1
    page.paginator.last_few = range(num_pages - few_visible + 1, num_pages + 1)
    page.paginator.last_few_border = num_pages - few_visible

    return page, paginator


def slugify(s):
    """
    Slugify string

    :param s: string to slugify
    :return: slugified string
    """

    return django_slugify(str(s).replace(u'ł', 'l').replace(u'Ł', 'L'))


def unix_time(datetime_):
    """
    :param datetime_: datetime object with or without timezone
    :return: unix time for given datetime
    """
    epoch = datetime.datetime.utcfromtimestamp(0)

    if timezone.is_aware(datetime_):
        epoch = timezone.make_aware(epoch, timezone.utc)

    delta = datetime_ - epoch

    return delta.total_seconds()
