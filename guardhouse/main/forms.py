from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import Account, Site

class SiteForm(ModelForm):
    class Meta(object):
        model = Site
        exclude = ('belongs_to', 'verification_state',)

    def clean_sentry_key(self):
        value = self.cleaned_data['sentry_key']
        if len(value) < 8:
            raise ValidationError(
                _("The value is too short. Enter at least 8 characters."))
        return value

class AccountForm(ModelForm):
    class Meta(object):
        model = Account
        exclude = ('owner', 'delegates')
