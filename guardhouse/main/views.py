from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import DeleteView
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
    form = AccountForm(request.POST if request.method == "POST" else None,
                       instance=account)
    if request.method == "POST":
        if form.is_valid():
            account = form.save(commit=False)
            account.owner = request.user
            account.save()
            messages.add_message(request, messages.INFO,
                                 _("Your account has been updated!"))
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
    context_object_name="sites"

class SiteDetailView(DetailView):
    model = Site

class SiteDeleteView(DeleteView):
    model = Site

    def delete(self, request, *args, **kwargs):
        response = super(SiteDeleteView, self).delete(request, *args, **kwargs)
        messages.add_message(request, messages.INFO, _("Site %s has been deleted."))
        return response

    def get_success_url(self):
        return reverse("sites")

class SiteVerifyView(DeleteView):
    """
    View to kick off site verification.
    (Hm a lot of code - not sure that CBV's are really an advantage)
    """
    model = Site
    template_name_suffix = '_confirm_verify'

    def post(self, *args, **kwargs):
        return self.verify(*args, **kwargs)

    def verify(self, request, **kwargs):
        self.object = self.get_object()

        self.object.verify(request)
        messages.add_message(
            request, messages.INFO,
            _("Verification started. You will be notified of the result shortly.")
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("sites")
