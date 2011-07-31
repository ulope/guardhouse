from django.forms import ModelForm
from .models import Site

class SiteForm(ModelForm):
    class Meta(object):
        model = Site
        exclude = ('verified',)

