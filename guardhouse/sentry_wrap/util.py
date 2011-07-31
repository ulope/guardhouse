import hmac
from django.utils.hashcompat import sha_constructor

def get_signature(message, timestamp, key):
    return hmac.new(key, '%s %s' % (timestamp, message), sha_constructor).hexdigest()
