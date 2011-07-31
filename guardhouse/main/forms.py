from django.forms import ModelForm
from .models import Account, Site

class SiteForm(ModelForm):
    class Meta(object):
        model = Site
        exclude = ('verified',)

class AccountForm(ModelForm):
    class Meta(object):
        model = Account
        exclude = ('owner', 'delegates')
