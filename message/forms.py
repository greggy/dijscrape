# -*- coding: utf-8 -*-

from django import forms
from message import scraper

from models import *


class ServerForm(forms.ModelForm):
    server_choice = forms.ChoiceField()

    class Meta:
        model = Server
        fields = ('server_choice', 'host', 'port')

    def __init__(self, *args, **kwargs):
        super(ServerForm, self).__init__(*args, **kwargs)
        self.fields['server_choice'].choices = [ (i[0], u'%s:%s' % (i[1], i[2])) for i in Server.objects.all()\
                                                        .values_list('id', 'host', 'port') ] + [(0, u'Other...')]

    def clean(self):
        cd = self.cleaned_data
        scrap = scraper.IMAPConnecter(host=cd['host'], port=cd['port'])
        check_connection = scrap.check_connection()
        if not check_connection:
            raise forms.ValidationError(u"Check if imap server's host/port correct!")
        return self.cleaned_data


class MailBoxForm(forms.ModelForm):
    class Meta:
        model = MailBox
        fields = ('username', 'password')

