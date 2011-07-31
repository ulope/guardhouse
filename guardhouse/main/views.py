from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import DeleteView, CreateView
from django.views.generic.simple import direct_to_template
from .decorators import skip_has_account_middleware
from .forms import AccountForm, SiteForm
from .models import Account, Site


@login_required
def dashboard(request):
    """
    Return all Sites that have unresolved messages associated.
    """
    sites = request.user.account.sites.filter(sentry_messages__message__group__status=0)
    return render(request, 'main/dashboard.html', {"sites": sites})


@login_required
def settings(request):
    return direct_to_template(request, 'main/settings.html')


@skip_has_account_middleware
@login_required
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


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class SiteListView(LoginRequiredMixin, ListView):
    model = Site
    context_object_name="sites"

    def get_queryset(self):
        return self.request.user.account.sites.all()


class SiteDetailView(LoginRequiredMixin, DetailView):
    model = Site

class SiteBaseModifyingMixin(object):
    model = Site

    def get_success_url(self):
        return reverse("sites")


class SiteDeleteView(LoginRequiredMixin, SiteBaseModifyingMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        messages.add_message(request, messages.INFO, _("Site has been deleted."))
        response = super(SiteDeleteView, self).delete(request, *args, **kwargs)
        return response

class SiteVerifyView(LoginRequiredMixin, SiteBaseModifyingMixin, DeleteView):
    """
    View to kick off site verification.
    (Hm a lot of code - not sure that CBV's are really an advantage)
    """
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


class SiteCreateView(LoginRequiredMixin, CreateView):
    model = Site
    form_class = SiteForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.belongs_to = self.request.user.account
        self.object.save()
        messages.add_message(
            self.request, messages.INFO,
            _("Site '%s' has been created") % self.object.name
        )
        return super(SiteCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse("sites")


