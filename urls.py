from django.conf.urls.defaults import *
from django.conf import *
from django.views.generic.simple import redirect_to

from django.contrib import admin

from registration.forms import RegistrationFormUniqueEmail


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'message.views.index', name='index'),
    url(r'^add_mailbox/$', 'message.views.add_mailbox', name='add-mailbox'),
    url(r'^add_mailbox/success/$', 'django.views.generic.simple.direct_to_template',
            {'template': 'add_mailbox_success.html'}, name='add-mailbox-success'),
    url(r'^rescrape/(\d+)/$', 'message.views.rescrape', name='rescrape'),

    url(r'^accounts/register/$', 'registration.views.register',
            {'form_class': RegistrationFormUniqueEmail}, name='registration_register'),
    (r'^accounts/', include('registration.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT} ),
)
