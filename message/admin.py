from django.contrib import admin

from models import *


class MessageAdmin(admin.ModelAdmin):
    model = Message
    list_display = ('sender', 'recipient', 'sender_name', 'sender_email', 'subject', 'payload', 'date_add',)
    

class PhoneNumberAdmin(admin.ModelAdmin):
    model = PhoneNumber
    list_display = ('name', 'email', 'value', 'preview', 'mailbox')
    
    search_fields = ['message__sender_name', 'message__sender_email', 'value',]
    
    def name(self, phoneNumber):
        return phoneNumber.message.sender_name
    
    def email(self, phoneNumber):
        return phoneNumber.message.sender_email
    
    def preview(self, phoneNumber):
        return phoneNumber.message.payload


class MailBoxAdmin(admin.ModelAdmin):
    list_display = ['username', 'user', 'status', 'last_scrape']


admin.site.register(Message, MessageAdmin)
admin.site.register(PhoneNumber, PhoneNumberAdmin)
admin.site.register(MailBox, MailBoxAdmin)

admin.site.register(Server)
admin.site.register(Account)
admin.site.register(Payment)
admin.site.register(RecurlyIPN)