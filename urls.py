from django.conf.urls.defaults import *
from django.conf import *
from django.views.generic.simple import redirect_to

from django.contrib import admin

from registration.forms import RegistrationFormUniqueEmail


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'message.views.index', name='index'),

    url(r'^accounts/register/$', 'registration.views.register',
            {'form_class': RegistrationFormUniqueEmail}, name='registration_register'),
    (r'^accounts/', include('registration.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT} ), 
)
