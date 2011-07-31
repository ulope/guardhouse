from django.contrib.admin import site
from sentry_wrap.models import SiteMessage

site.register(SiteMessage)
