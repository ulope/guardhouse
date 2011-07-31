from django.views.generic.simple import direct_to_template
from .decorators import skip_has_account_middleware


def dashboard(request):
    return direct_to_template(request, 'main/dashboard.html')


def settings(request):
    return direct_to_template(request, 'main/settings.html')


@skip_has_account_middleware
def account_setup(request):
    return direct_to_template(request, 'main/dashboard.html')
