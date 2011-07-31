from settings import *
from bundle_config import config

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": config['postgres']['host'],
        "PORT": int(config['postgres']['port']),
        "USER": config['postgres']['username'],
        "PASSWORD": config['postgres']['password'],
        "NAME": config['postgres']['database'],
    },
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '%s:%s' % (config['redis']['host'], config['redis']['port']),
        'OPTIONS': {
            'PASSWORD': config['redis']['password'],
        },
    },
}

# Celery
BROKER_BACKEND = "redis"
BROKER_HOST = config['redis']['host']
BROKER_PORT = int(config['redis']['port'])
BROKER_PASSWORD = config['redis']['password']
CELERY_RESULT_BACKEND = "redis"
REDIS_HOST = config['redis']['host']
REDIS_PORT = int(config['redis']['port'])
REDIS_PASSWORD = config['redis']['password']

COMPRESS_OFFLINE = True

LOGGING['handlers']['console']['level'] = "INFO"
