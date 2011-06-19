# -*- coding: utf-8 -*-

from celery.decorators import task


@task()
def mailbox_phones(x, y):
    return x + y