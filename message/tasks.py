# -*- coding: utf-8 -*-
from datetime import datetime

from celery.decorators import task

from django.template.loader import render_to_string

from message.models import MailBox
from scraper import Scraper
import settings


@task()
def mailbox_phones(host, username, password, user,
                   current_host, port=993, send_email=True):
    """
        Task will run when user save mailbox information.
    """
    print "Start scraper!!!"
    scrap = Scraper(host, username, password, user)
    ans = scrap.run()
    mailbox = MailBox.objects.get(username=username)
    mailbox.status = 2
    mailbox.save()

    if send_email:
        from django.core.mail import send_mail

        subject = render_to_string('scrape_email_subject.txt', {})
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message = render_to_string('scrape_email.txt', { 'host': current_host, 'count': ans })

        acc = user.get_profile()

        if acc.added_email:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [acc.added_email])
        else:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

    mailbox = MailBox.objects.get(username=username)
    mailbox.status = 3
    mailbox.last_scrape = datetime.now()
    mailbox.save()
    print "stoped"

    return ans


@task()
def test(x, y):
    print "Run test task!!!"
    return x + y