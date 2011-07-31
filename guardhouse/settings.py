# Django settings for guardhouse project.

from os import path
SITE_ROOT = path.dirname(path.realpath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Ulrich Petri', 'guardhouse@ulo.pe'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'guardhouse',
        'USER': 'httpd',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
    },
}

# Celery
BROKER_BACKEND = "redis"
BROKER_HOST = "localhost"
BROKER_PORT = 6379
BROKER_VHOST = "0"
CELERY_RESULT_BACKEND = "redis"
REDIS_HOST = "localhost"
REDIS_PORT = 6379


TIME_ZONE = 'Europe/Berlin'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

MEDIA_ROOT = path.join(SITE_ROOT, "media")

MEDIA_URL = '/media/'

STATIC_ROOT = path.join(SITE_ROOT, "static")

STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    path.join(SITE_ROOT, "web"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

try:
    # load secret key from file to keep it out of vcs
    with open(path.join(SITE_ROOT, ".secret"), "r") as secret:
        SECRET_KEY = secret.read()
except IOError:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        "You need to place a secret key in a file called '.secret' in the "
        "project root.\nFor example:\n\t$ ./manage.py generate_secret_key > .secret"
    )

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'main.middleware.HasAccountMiddleware',
    'main.middleware.SiteVerificationCompletionMiddleware',
)

SESSION_ENGINE = "redis_sessions.backends.redis"

ROOT_URLCONF = 'guardhouse.urls'

TEMPLATE_DIRS = (
    path.join(SITE_ROOT, "templates"),
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    #'socialauth.auth_backends.OpenIdBackend',
    #'socialauth.auth_backends.TwitterBackend',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_extensions',
    'compressor',
    'south',
    'sentry',
    'sentry.client',
    #'openid_consumer',
    #'socialauth',
    'djcelery',

    'content',
    'main',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            format: '%(levelname)s %(name)s(%(lineno)d): %(message)s',
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'default'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'south': {
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

# socialauth stuff
OPENID_REDIRECT_NEXT = '/accounts/openid/done/'

OPENID_SREG = {"requred": "nickname, email, fullname",
               "optional":"postcode, country",
               "policy_url": ""}

#example should be something more like the real thing, i think
OPENID_AX = [{"type_uri": "http://axschema.org/contact/email",
              "count": 1,
              "required": True,
              "alias": "email"},
             {"type_uri": "http://axschema.org/schema/fullname",
              "count":1 ,
              "required": False,
              "alias": "fname"}]

OPENID_AX_PROVIDER_MAP = {'Google': {'email': 'http://axschema.org/contact/email',
                                     'firstname': 'http://axschema.org/namePerson/first',
                                     'lastname': 'http://axschema.org/namePerson/last'},
                          'Default': {'email': 'http://axschema.org/contact/email',
                                      'fullname': 'http://axschema.org/namePerson',
                                      'nickname': 'http://axschema.org/namePerson/friendly'}
                          }

try:
    from local_settings import *
except ImportError:
    pass

import djcelery
djcelery.setup_loader()
