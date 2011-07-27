# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.auth import login
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from const import *


class Message(models.Model):
    user = models.ForeignKey(User)
    sender = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255) 
    sender_name = models.CharField(max_length=255)
    sender_email = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    payload = models.TextField()
    date_add = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.sender_name

    
class PhoneNumber(models.Model):
    user = models.ForeignKey(User)
    message = models.ForeignKey(Message, related_name='phone_numbers')
    value = models.CharField('Phone', max_length=16)
    mailbox = models.ForeignKey('MailBox')

    def __unicode__(self):
        return self.value


class Server(models.Model):
    u'''
        Collection of imap servers shared with all users.
    '''
    host = models.CharField(max_length=100)
    port = models.PositiveIntegerField(default=993)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return u'%s:%s' % (self.host, self.port)

    class Meta:
        unique_together = (('host', 'port'),)


STATUS_CHOICE = (
    (1, u'Just Added'),
    (2, u'In Progress'),
    (3, u'Finished')
)

class MailBox(models.Model):
    u'''
        User's mailboxes.
    '''
    user = models.ForeignKey(User)
    server = models.ForeignKey(Server)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=100, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICE, default=1)
    last_scrape = models.DateTimeField(default=datetime.now())
    use_oauth = models.BooleanField(default=False)
    oauth_token = models.CharField(max_length=200, blank=True)
    oauth_secret = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return u'%s %s %s' % (self.server, self.username, self.status)

    class Meta:
        #unique_together = (('username', 'password'),)
        verbose_name = u'MailBox'
        verbose_name_plural = u'MailBoxes'


class Account(models.Model):
    user = models.OneToOneField(User)
    mode = models.PositiveSmallIntegerField(choices=MODE_CHOICE, default=1)
    paid_until = models.DateTimeField(blank=True, null=True)
    added_email = models.EmailField(blank=True, null=True)

    def __unicode__(self):
        return self.user.username


class Payment(models.Model):
    user = models.ForeignKey(User)
    payment_type = models.PositiveSmallIntegerField(choices=TYPE_CHOICE, default=1)
    date_add = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __unicode__(self):
        return self.user.username


class RecurlyIPN(models.Model):
    email = models.EmailField()
    #username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    payment_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date_add = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return self.email


def create_account(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        Account.objects.create(user=user, added_email=user.email)

post_save.connect(create_account, sender=User)
