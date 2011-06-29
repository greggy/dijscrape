# -*- coding: utf-8 -*-
from calendar import monthrange
from datetime import date

from django import forms
from django.contrib.localflavor.us.us_states import STATE_CHOICES

from message import scraper
from models import *
from utils import CreditCard

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


class AddEmailForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('added_email',)


CARD_CHOICES = (
    ('American Express', 'American Express'),
    ('Visa', 'Visa'),
    ('Mastercard', 'Mastercard'),
    ('Discover', 'Discover')
)

class RecurlyForm(forms.ModelForm):
    address1 = forms.CharField(label='Address 1')
    address2 = forms.CharField(label='Address 2', required=False)
    city = forms.CharField(label='City', required=False)
    state = forms.ChoiceField(choices=STATE_CHOICES, label='State')
    zip = forms.CharField(max_length=6, label='Zip Code')
    country = forms.CharField(max_length=2, label='Country', initial='US')
    #type = forms.ChoiceField(choices=CARD_CHOICES, label='Credit Card Type')
    number = forms.CharField(label='Card Number')
    verification_value = forms.CharField(label='CCV Code')
    year = forms.CharField(label='Expired Year')
    month = forms.CharField(label='Expired Month')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'address1', 'address2', 'city', 'state', 'zip',
            'country', 'number', 'verification_value', 'year', 'month')

    '''
    def clean_number(self):
        """ Check if credit card is valid. """
        credit_number = self.cleaned_data['number']
        card = CreditCard(credit_number, self.cleaned_data['type'])
        results, msg = card.verifyCardTypeandNumber()
        if not results:
            raise forms.ValidationError(msg)
        return credit_number
    '''

    def clean(self):
        """ Check if credit card has expired. """
        month = self.cleaned_data.get('month')
        year = self.cleaned_data.get('year')
        if not month or not year:
            raise forms.ValidationError('Enter correct expired date.')
        max_day = monthrange(int(year), int(month))[1]
        if date.today() > date(year=int(year), month=int(month), day=max_day):
            raise forms.ValidationError('Your card has expired.')
        return self.cleaned_data

    '''
    def clean_ccv(self):
        """ Validate a proper CCV is entered. Remember it can have a leading 0 so don't convert to int and return it"""
        try:
            check = int(self.cleaned_data['ccv'])
            return self.cleaned_data['ccv']
        except ValueError:
            raise forms.ValidationError('Invalid ccv.')
    '''


