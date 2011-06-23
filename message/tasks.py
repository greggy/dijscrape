# -*- coding: utf-8 -*-

from celery.decorators import task

from django.contrib.auth.models import User

from scraper import Scraper


@task()
def mailbox_phones(host, username, password, user, port=993):
    """
    Task will run when user save mailbox information.=
    """
    print "Start scraper!!!"
    scrap = Scraper(host, username, password, user)
    ans = scrap.run()
    #TODO: Write email sender
    return ans


@task()
def test(x, y):
    print "Run test task!!!"
    return x + y