from django.db import models
from django.contrib.auth.models import User


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
    (3, u'Invalid'),
    (4, u'Finished')
)

class MailBox(models.Model):
    u'''
        User's mailboxes.
    '''
    user = models.ForeignKey(User)
    server = models.ForeignKey(Server)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=100)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICE, default=1)
    last_scrape = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u'%s %s %s' % (self.server, self.username, self.status)

