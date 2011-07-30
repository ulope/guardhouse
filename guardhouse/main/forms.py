from django.forms import ModelForm
from .models import Site

class SiteForm(ModelForm):
    model = Site
    exclude = ('verified',)

