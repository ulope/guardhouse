from django.utils.translation import ugettext as _
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from .models import Account, Site

class HasAccountMiddleware(object):
    """Force new users to set up account information"""
    def process_view(self, request, view_func, view_args, view_kwargs):
        if (hasattr(view_func, "skip_has_account_middleware") or
            request.path.startswith("/auth")):
            # Skip middleware for allowed views
            return
        try:
            if request.user.is_anonymous():
                return
            else:
                if request.user.is_staff:
                    # Staff can do anything :)
                    return
                if Account.objects.filter(owner=request.user).exists():
                    # User already has an account set up
                    return
                elif request.user.authorized_for.exists():
                    # User is authorized for at least one other account -> doesn't
                    # have to have his own.
                    return
            # User is neither authorized for other accounts nor has his own
            # account -> redirect to account setup
            return redirect("account_setup", force="new")
        except AttributeError:
            # No user on request 
            raise ImproperlyConfigured(
                "%s needs django's 'AuthenticationMiddleware' to be enabled."
            )


class SiteVerificationCompletionMiddleware(object):
    def process_request(self, request):
        verify_runs = request.session.get('verify_runs', [])
        keep_runs = []
        for run in verify_runs:
            site = Site.objects.get(pk=run.site_id)
            if run.task.ready():
                if run.task.failed():
                    messages.add_message(
                        request, messages.WARNING,
                        _(u"Site verification for site '%s' failed. Click to "
                           "retry.") % site.name,
                        "retry_verify"
                    )
                    request.session.setdefault("retry_site_ids", []).append(site.pk)
                else:
                    messages.add_message(
                        request, messages.INFO,
                        _(u"Site verification for site '%s' succeeded."
                         ) % site.name
                    )
            else:
                # Run hasn't finised, keep it in the list
                keep_runs.append(run)
        request.session['verify_runs'] = keep_runs
