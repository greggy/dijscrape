# -*- coding: utf-8 -*-
import socket
#import threading

import datetime
import rfc822
import time
import re
import imaplib
import sys
import os
from email.parser import HeaderParser

from django.conf import settings
from django.utils.encoding import smart_unicode

from models import *
from utils import num, uniqify

nanp_pattern = '(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'
number_re = re.compile(nanp_pattern)
email_re = re.compile('("?([a-zA-Z 0-9\._\-]+)"?\s+)?<?([a-zA-Z0-9\._\-]+@[a-zA-Z0-9\._\-]+)>?')
    

class Analizer:
    def __init__(self, imap, number, user):
        #threading.Thread.__init__(self)
        self.number = number
        self.imap = imap
        self.user = user

    def search_phone(self):
        print 'processing message num: ' + str(self.number)
        try:
            response, message_data = self.imap.fetch(self.number, '(BODY.PEEK[HEADER])')
        except:
            print "Exception in HEADER"
            return False

        raw_message = message_data[0][1] # message_data, the data structure returned by imaplib, encodes some data re: the request type
        header = HeaderParser().parsestr(raw_message)
        if header['Content-Type'] is not None and 'multipart' in header['Content-Type']:
            print "INcorrect content type"
            return False # right now we're just skipping any multipart messages. this needs to be rewritten to parse the text parts of said messgs.
        try:
            response, message_data = self.imap.fetch(self.number, '(BODY.PEEK[TEXT])')
        except:
            print "Exception in TEXT"
            return False

        text_payload = message_data[0][1]
        found_digits = number_re.findall(text_payload)

        if found_digits != []:
            print "Message %d has numbers." % num(self.number)
            print found_digits
            ### need to cast the Date header into a MySQL object.
            ts = header['Date']
            print 'header date: ' + str(ts)
            if rfc822.parsedate_tz(ts) is not None: #making sure the date header is not empty
                ts_tuple = rfc822.parsedate_tz(ts)
            #perhaps in the future we can intead set the ts_tuple to (0,0,0,0,0,0,0) and interpret it in the UI as 'no date header'. assuming that is actually the problem.
            #otherwise, we're setting it to the date of the most recently received email... and this could get awkward. #TODO: fix this once the UI is ready.
            ts_python_datetime = datetime.datetime(*(ts_tuple[0:6]))
            ts_mysql_datetime = ts_python_datetime.isoformat(' ')

            print 'about to insert into the database'
            ### sometimes it fails due to unicode issues
            print 'about to parse name and email from header'
            print 'header: ' + str(header['From'])
            try:
                name, email = email_re.match(header['From']).groups()[1:3]
            except:
                print "Unexpected error:", sys.exc_info()[0]
                return False
            print 'parsing name and email from FROM header: ' + str(name) + ', ' + str(email)

            try:
                m = Message(
                    user=self.user,
                    sender=header['From'][:255],
                    recipient=header['To'][:255],
                    sender_name=str(name)[:255],
                    sender_email=email[:255],
                    subject=header['Subject'][:255],
                    date_add=ts_mysql_datetime,
                    payload=str(text_payload[:65534])
                )
                m.save()
            except Exception as e:
                print "Can't save", "test", e
            pure_digits = uniqify(map(''.join, found_digits)) # the phone number regexp will create lists like ['','650','555','1212']. this collapses the list into a string.

            print 'We found pure digits: ' + str(pure_digits)
            for phone_number in pure_digits:
                if len(str(phone_number)) > 7:  # for now, we want numbers with area codes only.
                    print phone_number
                    PhoneNumber(value=phone_number, message=m, user=self.user).save()


class IMAPConnecter:
    def __init__(self, host, port, email=False, password=False, ssl=True):
        self.email = email
        self.password = password
        self.host = host
        self.port = port
        self.ssl = ssl
        self.mail_count = 0

    def get_connection(self):
        imap = imaplib.IMAP4_SSL(self.host, self.port)
        imap.login(self.email, self.password)
        response, mail_count = imap.select()
        self.mail_count = int(mail_count[0])
        return imap

    def check_connection(self):
        u'''
            Checker if server's host, port correct.
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.host, self.port))
            s.shutdown(2)
            return True
        except:
            return False

    def get_mail_count(self):
        return self.mail_count


class Scraper:
    u'''
        port 993 - SSL connection
        port 143 - simple connection (unsecured)
    '''
    def __init__(self, host, email, password, user, port=993, ssl=True):
        self.email = email
        self.password = password
        self.host = host
        self.port = port
        self.user = user
        self.analizers = []
                   
    def run(self):
        print 'Connecting to the Google IMAP server'
        conn = IMAPConnecter(self.host, self.port, self.email, self.password)
        imap = conn.get_connection()

        print "Messages to process:", conn.get_mail_count()

        response, list_of_messages = imap.search(None, 'ALL')
        mlist = list_of_messages[0].split()

        for item in range(0, conn.get_mail_count()):
            analizer = Analizer(imap, mlist[item], self.user)
            analizer.search_phone()

        return conn.get_mail_count()
