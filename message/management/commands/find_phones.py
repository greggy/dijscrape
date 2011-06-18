from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from message.scraper import Scraper
import time


class Command(BaseCommand):

    def handle(self, *args, **options):
        start_time = time.time()
        Scraper(settings.EMAIL, settings.EMAIL_PASSWD).run()
        print "Done in %.3f seconds" % (time.time() - start_time)
       