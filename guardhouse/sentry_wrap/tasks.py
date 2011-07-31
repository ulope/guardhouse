import base64
import logging
import pickle
import datetime
from django.utils.encoding import smart_str
from sentry.models import GroupedMessage
import warnings
from django.http import HttpResponseBadRequest, HttpResponseGone, HttpResponse, HttpResponseForbidden
from celery.decorators import task
from django.shortcuts import get_object_or_404
from sentry.utils import parse_auth_header, json, is_float
import time
import zlib
from main.models import Site
from sentry_wrap.models import SiteMessage

from sentry_wrap.util import get_signature


# This code is largely taken from sentry.views.store
@task()
def input_message(data, format, key, http_auth, raw_post_data):
    if http_auth.startswith('Sentry'):
        auth_vars = parse_auth_header(http_auth)

        signature = auth_vars.get('sentry_signature')
        timestamp = auth_vars.get('sentry_timestamp')

        format = 'json'

        data = raw_post_data

        # Signed data packet
        if signature and timestamp:
            try:
                timestamp = float(timestamp)
            except ValueError:
                raise ValueError('Invalid timestamp')

            if timestamp < time.time() - 3600: # 1 hour
                raise ValueError('Message has expired')

            return find_site_for_signature.delay(data, format, timestamp, signature)
        else:
            raise ValueError('Unauthorized')
    else:
        if not data:
            raise ValueError('Missing data')

        if format not in ('pickle', 'json'):
            raise ValueError('Invalid format')

        # Legacy request (deprecated as of 2.0)
        site = get_object_or_404(Site, sentry_key=key)
        if key != site.sentry_key:
            warnings.warn('A client is sending the `key` parameter, which will be removed in Sentry 2.0', DeprecationWarning)
            raise ValueError('Invalid credentials')

        store_message.delay(data, format, site)

@task()
def find_site_for_signature(data, format, timestamp, signature):
    """
    Ugly. We have to loop trough all Sites to know if we want to accept the
    message because newer sentry versions don't send KEY anymore.
    """
    found_site = None
    for site in Site.objects.all():
        sig_hmac = get_signature(data, timestamp)
        if sig_hmac == signature:
            found_site = site
            break
    else:
        raise ValueError('Invalid signature')
    return store_message.delay(data, format, found_site)

@task()
def store_message(data, format, site):
    logger = logging.getLogger('sentry.server')

    try:
        try:
            data = base64.b64decode(data).decode('zlib')
        except zlib.error:
            data = base64.b64decode(data)
    except Exception, e:
        # This error should be caught as it suggests that there's a
        # bug somewhere in the client's code.
        logger.exception('Bad data received')
        raise ValueError('Bad data decoding request (%s, %s)' % (e.__class__.__name__, e))

    try:
        if format == 'pickle':
            data = pickle.loads(data)
        elif format == 'json':
            data = json.loads(data)
    except Exception, e:
        # This error should be caught as it suggests that there's a
        # bug somewhere in the client's code.
        logger.exception('Bad data received')
        raise ValueError('Bad data reconstructing object (%s, %s)' % (e.__class__.__name__, e))

    # XXX: ensure keys are coerced to strings
    data = dict((smart_str(k), v) for k, v in data.iteritems())

    if'timestamp' in data:
        if is_float(data['timestamp']):
            try:
                data['timestamp'] = datetime.datetime.fromtimestamp(float(data['timestamp']))
            except:
                logger.exception('Failed reading timestamp')
                del data['timestamp']
        elif not isinstance(data['timestamp'], datetime.datetime):
            if '.' in data['timestamp']:
                format = '%Y-%m-%dT%H:%M:%S.%f'
            else:
                format = '%Y-%m-%dT%H:%M:%S'
            if 'Z' in data['timestamp']:
                # support GMT market, but not other timestamps
                format += 'Z'
            try:
                data['timestamp'] = datetime.datetime.strptime(data['timestamp'], format)
            except:
                logger.exception('Failed reading timestamp')
                del data['timestamp']

    message = GroupedMessage.objects.from_kwargs(**data)
    SiteMessage.objects.create(site=site, message=message)
