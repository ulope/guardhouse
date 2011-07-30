from django.contrib.admin import site
from .models import Account, Site

site.register(Account)
site.register(Site)
