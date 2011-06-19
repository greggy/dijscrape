# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from lib import render_to
from message import tasks
from models import *
from forms import *


@login_required()
@render_to('index.html')
def index(request):
    return {}



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
            cd = sform.cleaned_data
            try:
                server = Server.objects.get(host=cd['host'], port=cd['port'])
            except Server.DoesNotExist:
                server = sform.save()
            mailbox = mform.save(commit=False)
            mailbox.user = request.user
            mailbox.server = server
            mailbox.save()
            # add asynchronous task
            tasks.mailbox_phones(23, 45)
            return redirect(reverse('add-mailbox-success'))
    else:
        context = {
            'username': request.user.email
        }
        sform = ServerForm()
        mform = MailBoxForm(initial=context)
    return {'sform': sform, 'mform': mform}