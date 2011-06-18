from django.db import models


class Message(models.Model):
    sender = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255) 
    sender_name = models.CharField(max_length=255)
    sender_email = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    payload = models.TextField()
    date = models.DateTimeField()
    
    
class PhoneNumber(models.Model):
    message = models.ForeignKey(Message, related_name='phoneNumbers')
    value = models.CharField('Phone', max_length=16)  
