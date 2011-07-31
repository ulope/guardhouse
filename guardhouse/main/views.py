from django.utils.translation import ugettext as _
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic.simple import direct_to_template
from .decorators import skip_has_account_middleware
from .forms import AccountForm
from .models import Account, Site


def dashboard(request):
    return direct_to_template(request, 'main/dashboard.html')


def settings(request):
    return direct_to_template(request, 'main/settings.html')


@skip_has_account_middleware
def account_setup(request, force=False):
    account = None
    try:
        account = request.user.account
    except Account.DoesNotExist:
        pass
    form = AccountForm(request.POST if request.method == "POST" else None, instance=account)
    if request.method == "POST":
        if form.is_valid():
            account = form.save(commit=False)
            account.owner = request.user
            account.save()
            messages.add_message(request, messages.INFO, _("Your account has been updated!"))
            return redirect("account_setup")
    else:
        if force:
            messages.add_message(
                request, messages.WARNING,
                _("You need to configure your account on this page before you can use the site.")
            )
    return render(request, 'main/account.html', {"form": form})


class SiteListView(ListView):
    model = Site
    context_object_name="sites"#
    