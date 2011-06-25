# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect

from lib import render_to
from message import tasks
from models import *
from forms import *


@login_required()
@render_to('index.html')
def index(request):
    mailboxes = MailBox.objects.filter(user=request.user)
    return {'mailboxes': mailboxes}


@login_required()
def rescrape(request, mailbox_id):
    mailbox = MailBox.objects.get(pk=mailbox_id)
    tasks.mailbox_phones.delay(mailbox.server.host, mailbox.username, mailbox.password, request.user)
    return HttpResponse("OK")


@login_required()
@render_to('add_mailbox.html')
def add_mailbox(request):
    u'''
        Add mailbox to db and send asynchronous task.
        Check if imap server accept connection.
        Add server host, port to db if it not exist yet.
    '''
    if request.method == 'POST':
        sform = ServerForm(request.POST)
        mform = MailBoxForm(request.POST)
        if sform.is_valid() and mform.is_valid():
            scd = sform.cleaned_data
            mcd = mform.cleaned_data
            print scd, mcd
            try:
                server = Server.objects.get(host=scd['host'], port=scd['port'])
            except Server.DoesNotExist:
                server = sform.save()
            mailbox = mform.save(commit=False)
            mailbox.user = request.user
            mailbox.server = server
            mailbox.save()
            # add asynchronous task
            tasks.mailbox_phones.delay(scd['host'], mcd['username'], mcd['password'], request.user)
            #tasks.test.delay(23, 44)
            return redirect(reverse('add-mailbox-success'))
        else:
            print sform.errors, mform.errors
    else:
        context = {
            'username': request.user.email
        }
        sform = ServerForm()
        mform = MailBoxForm(initial=context)
    return {'sform': sform, 'mform': mform}