# -*- coding: utf-8 -*-
import base64
import urllib2
import uuid

from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import payment_was_successful

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
            return redirect(reverse('add-mailbox-success', args=[mailbox.id]))
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



@login_required()
@render_to('add_mailbox_success.html')
def add_mailbox_success(request, mailbox_id):
    mailbox = get_object_or_404(MailBox, pk=mailbox_id, user=request.user)
    if request.method == 'POST':
        form = AddEmailForm(request.POST, instance=mailbox.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('index'))
    else:
        form = AddEmailForm(instance=mailbox.user)
    return {'form': form}


@login_required()
@render_to('search.html')
def search(request):
    query = request.GET.get('q', '')
    phones = PhoneNumber.objects.filter(Q(value__icontains=query, user=request.user) |
                                       Q(message__sender_name__icontains=query, user=request.user) |
                                       Q(message__sender_email__icontains=query, user=request.user) |
                                       Q(message__subject__icontains=query, user=request.user) |
                                       Q(message__payload__icontains=query, user=request.user)
    )
    return {'phones': phones}


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
    plan = request.GET.get('plan')
    refferer = request.META.get('HTTP_REFERER')
    user = request.user
    if plan and refferer and 'recurly.com' in refferer:
        if plan == 'month':
            amount = 9
        elif plan == 'year':
            amount = 99
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


@login_required()
@render_to('set_recurly.html')
def set_recurly(request):
    amount = request.GET.get('amount', 9)
    user = request.user
    if request.method == 'POST':
        form = RecurlyForm(request.POST, instance=request.user)
        if form.is_valid():
            cd = form.cleaned_data
            form.save()
            xml_context = {
                'amount': int(amount) * 100,
                'account': str(uuid.uuid4()).replace('-', '')[:8],
                'username': user.username,
                'email': cd['email'],
                'first_name': cd['first_name'],
                'last_name': cd['last_name'],
                'address1': cd['address1'],
                'address2': cd['address2'],
                'city': cd['city'],
                'state': cd['state'],
                'zip': cd['zip'],
                'country': cd['country'],
                'ip_address': request.META['REMOTE_ADDR'] if request.META.get('REMOTE_ADDR') else request.META.get('HTTP_X_FORWARDED_FOR', '8.8.8.8'),
                'number': cd['number'],
                'vv': cd['verification_value'],
                'year': cd['year'],
                'month': cd['month'],
            }
            xml = render_to_string('transaction.xml', xml_context)

            url = 'https://%s.recurly.com/transactions' % settings.RSUBDOMAIN
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            header = urllib2.Request(url=url, data=xml)
            #header.get_method = 'POST'
            header.add_header('Accept', 'application/xml')
            header.add_header('Content-Type', 'application/xml; charset=utf-8')
            header.add_header('Authorization', 'Basic %s' % base64.standard_b64encode('%s:%s' % (settings.RUSER, settings.RPASSWD)))

            try:
                response = opener.open(header)
                xml_response = response.read()
            except urllib2.HTTPError, e:
                xml_response = e.read()
            except urllib2.URLError, e:
                print e

            #print xml_response
            if xml_response is '':
                response = None
            else:
                from xml.etree.ElementTree import fromstring

                tree = fromstring(xml_response)
                try:
                    status = tree.find('status')
                    amount = tree.find('amount_in_cents')
                    print status.text

                    Payment.objects.create(user=user, amount=(int(amount.text) / 100))
                    acc = user.get_profile()
                    dt_now = datetime.now()
                    period = PAYMENT_PERIOD[float(int(amount.text) / 100)]
                    if period == 'month':
                        acc.paid_until = dt_now.replace(month=dt_now.month+1)
                        acc.mode = 2
                    elif period == 'year':
                        acc.paid_until = dt_now.replace(year=dt_now.year+1)
                        acc.mode = 3
                    acc.save()

                    return redirect(reverse(settings.RETURN_URL))
                except:
                    error = tree.find('error')
                    print "Transaction error: %s." % error.text
                    raise Http404

    else:
        form = RecurlyForm(instance=request.user)
    return {'form': form}

