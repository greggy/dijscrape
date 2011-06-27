# -*- coding: utf-8 -*-
from datetime import datetime
import uuid
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import payment_was_successful

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from lib import render_to
from message import tasks
from models import *
from forms import *
from const import *


@login_required()
@render_to('index.html')
def index(request):
    mailboxes = MailBox.objects.filter(user=request.user)
    dt_now = datetime.now()
    acc = request.user.get_profile()
    if acc.paid_until and acc.paid_until < dt_now:
        acc.mode = 1
        acc.save()
    return {'mailboxes': mailboxes}


@login_required()
def rescrape(request, mailbox_id):
    mailbox = MailBox.objects.get(pk=mailbox_id)
    tasks.mailbox_phones.delay(mailbox.server.host, mailbox.username,
                               mailbox.password, request.user, request.get_host())
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
            tasks.mailbox_phones.delay(scd['host'], mcd['username'], mcd['password'], request.user, request.get_host())
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



@login_required()
@render_to('add_mailbox.html')
def edit_mailbox(request, mailbox_id):
    mailbox = get_object_or_404(MailBox, pk=mailbox_id, user=request.user)
    if request.method == 'POST':
        sform = ServerForm(request.POST, instance=mailbox.server)
        mform = MailBoxForm(request.POST, instance=mailbox)
        if sform.is_valid() and mform.is_valid():
            scd = sform.cleaned_data
            mcd = mform.cleaned_data
            try:
                server = Server.objects.get(host=scd['host'], port=scd['port'])
            except Server.DoesNotExist:
                server = sform.save()
            mailbox = mform.save(commit=False)
            mailbox.user = request.user
            mailbox.server = server
            mailbox.save()
            return redirect(reverse('index'))
    else:
        sform = ServerForm(instance=mailbox.server)
        mform = MailBoxForm(instance=mailbox)
    return {'sform': sform, 'mform': mform}


# Payment
@login_required()
@render_to('set_paypal.html')
def set_paypal(request):
    u'''
        Create PayPal form to send user to pay.
    '''
    amount = request.POST.get('amount', 9)
    notify_url = "https://%s%s" % (request.get_host(), '/payment/notify/')
    return_url = "http://%s%s" % (request.get_host(), reverse(settings.RETURN_URL))
    cancel_url = "http://%s%s" % (request.get_host(), reverse(settings.CANCEL_URL))
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": amount,
        "item_name": "Subscription of LostPhoneNumbers",
        "invoice": "%s_%s" % (request.user.id, str(uuid.uuid4()).replace('-', '')[:8]),
        "notify_url": notify_url,
        "return_url": return_url,
        "cancel_return": cancel_url,
    }
    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    return {'pp_form': form, 'amount': amount}


@csrf_exempt
@login_required()
@render_to('payment_status.html')
def payment_status(request, status):
    return {'status': status}


def ipn_success(sender, **kwargs):
    u'''
        Signal to enable subscription. This signal catched by PP notify url response.
    '''
    ipn_obj = sender
    user = User.objects.get(pk=ipn_obj.invoice.split('_')[0])
    amount=ipn_obj.mc_gross
    payment = Payment.objects.create(user=user, amount=amount)
    acc = user.get_profile()
    dt_now = datetime.now()
    period = PAYMENT_PERIOD[float(amount)]
    if period == 'month':
        acc.paid_until = dt_now.replace(month=dt_now.month+1)
        acc.mode = 2
    elif period == 'year':
        acc.paid_until = dt_now.replace(year=dt_now.year+1)
        acc.mode = 3
    acc.save()
    print "Mode was changed for %s." % user.username

payment_was_successful.connect(ipn_success)
