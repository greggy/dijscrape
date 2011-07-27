# Django settings for flights project.
import os.path
import sys

ROOT_PATH = os.path.dirname(__file__)

sys.path.insert(0,  os.path.join(ROOT_PATH, '..'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', #postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': './test.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "templates", "site_media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'f6h+js%gs59=$x7^kr1wj8$jkj4q+ghk#zz$kj#7^4v#q*y95h'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(ROOT_PATH, './templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',

    'message',

    'registration',
    'south',
    'paypal.standard.ipn',
)

MAX_THREAD = 5

ACCOUNT_ACTIVATION_DAYS = 3
LOGIN_REDIRECT_URL = '/'

AUTH_PROFILE_MODULE = "message.Account"

# email settings
DEFAULT_FROM_EMAIL = 'dijscrape@gmail.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'dijscrape@gmail.com'
EMAIL_HOST_PASSWORD = 'qw3rty123'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# payment settings PayPal
RETURN_URL = 'payment-return'
CANCEL_URL = 'payment-cancel'
PAYPAL_RECEIVER_EMAIL = 'greg_1309080665_biz@dobroe.ru'

# Recurly
RUSER = 'api-test@greg-test.com'
RPASSWD = '011f4db3597449caa368d7016776d0dd'
RSUBDOMAIN = 'greg-test'

# Google API
GOOGLE_TOKEN = 'dijscrape.ep.io'
GOOGLE_SECRET = 'olQ6O5WoRJ4hIPKZ9rO9VlNE'

REQUEST_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetRequestToken'
AUTHORIZATION_URL = 'https://www.google.com/accounts/OAuthAuthorizeToken'
ACCESS_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetAccessToken'

try:
    from local_settings import *
except ImportError:
    pass

