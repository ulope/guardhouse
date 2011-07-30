from django.shortcuts import render_to_response
from .decorators import skip_has_account_middleware


def dashboard(request):
    return render_to_response('main/dashboard.html')


def settings(request):
    return render_to_response('main/settings.html')


@skip_has_account_middleware
def account_setup(request):
    return render_to_response('main/dashboard.html')
