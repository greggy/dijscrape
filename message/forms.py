# -*- coding: utf-8 -*-

from django import forms

from message import scraper
from models import *

from registration.forms import RegistrationFormUniqueEmail
from registration.models import RegistrationProfile


class RegisterForm(RegistrationFormUniqueEmail):
    def save(self, profile_callback=None):
        new_user = RegistrationProfile.objects.create_inactive_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'])

        new_account = Account.objects.create(
            user=new_user
        )

        return new_user


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
        if cd['server_choice'] == u'0' and cd.get('host') and cd.get('port'):
            scrap = scraper.IMAPConnecter(host=cd['host'], port=cd['port'])
            check_connection = scrap.check_connection()
            if not check_connection:
                raise forms.ValidationError(u"Check if imap server's host/port correct!")
        return cd


class MailBoxForm(forms.ModelForm):
    class Meta:
        model = MailBox
        fields = ('username', 'password')

