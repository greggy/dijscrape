from django.conf.urls.defaults import *
from django.conf import *
from django.views.generic.simple import redirect_to

from django.contrib import admin

from message.forms import RegisterForm


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'message.views.index', name='index'),
    url(r'^search/$', 'message.views.search', name='search'),
    url(r'^add_mailbox/$', 'message.views.add_mailbox', name='add-mailbox'),
    url(r'^edit_mailbox/(\d+)/$', 'message.views.edit_mailbox', name='edit-mailbox'),
    url(r'^add_mailbox_success/(\d+)/$', 'message.views.add_mailbox_success', name='add-mailbox-success'),
    url(r'^rescrape/(\d+)/$', 'message.views.rescrape', name='rescrape'),

    # payment urls
    url(r'^payment/$', 'django.views.generic.simple.direct_to_template',
            {'template': 'payment.html'}, name='payment'),
    url(r'^payment/success/$', 'message.views.payment_status', {'status': 'success'}, name='payment-return'),
    url(r'^payment/cancel/$', 'message.views.payment_status', {'status': 'cancel'}, name='payment-cancel'),
    url(r'^payment/paypal/$', 'message.views.set_paypal', name='payment-paypal'),
    url(r'^payment/recurly/$', 'message.views.set_recurly', name='payment-recurly'),
    (r'^payment/recurly/notify/$', 'message.views.recurly_notify'),
    (r'^payment/notify/$', include('paypal.standard.ipn.urls')),

    url(r'^accounts/register/$', 'registration.views.register',
            {'form_class': RegisterForm}, name='registration_register'),
    (r'^accounts/', include('registration.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT} ),
)
