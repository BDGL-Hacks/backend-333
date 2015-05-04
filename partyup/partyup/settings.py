"""
Django settings for partyup project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# os.environ['DJANGO_SETTINGS_MODULE'] = 'partyup.settings'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$&2$p=s9!6v0l$p_x_ct@rpznb)-64pc-e@g4f1rc%)=lxeed@'

# SECURITY WARNING: don't run with debug turned on in production!
import sys
try:
    is_dev = (sys.argv[1] == 'runserver')
except:
    is_dev = False
DEBUG = is_dev

TEMPLATE_DEBUG = is_dev

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'push_notifications',
    'web',
)

PUSH_NOTIFICATIONS_SETTINGS = {
    "APNS_CERTIFICATE": "pushInfo/ck.nokey.pem",
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.ProcessExceptionMiddleware',
)

ROOT_URLCONF = 'partyup.urls'

WSGI_APPLICATION = 'partyup.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'partyup',
        'USER': 'partyup',
        'PASSWORD': 'blakedavidgrahamlance',
        'HOST': 'localhost'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# Name of AWS S3 bucket. Used for picture uploading, downloading, and etc.
# S3_BUCKET = 'partyup'

# Server IP address. Used for setting destination for API calls
import urllib, re
if is_dev:
    DESTINATION = 'http://localhost:8000'
else:
    # Look up public ip address
    data = str(urllib.urlopen('http://checkip.dyndns.com/').read())
    DESTINATION = 'http://' + re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)
