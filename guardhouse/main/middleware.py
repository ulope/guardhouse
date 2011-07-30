from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from .models import Account

class HasAccountMiddleware(object):
    """Force new users to set up account information"""
    def process_view(self, request, view_func, view_args, view_kwargs):
        if hasattr(view_func, "skip_has_account_middleware"):
            # Skip middleware for allowed views
            return
        try:
            if request.user.is_anonymous():
                return
            else:
                if Account.objects.filter(owner=request.user).exists():
                    # User already has an account set up
                    return
                elif request.user.authorized_for.exists():
                    # User is authorized for at least one other account -> doesn't
                    # have to have his own.
                    return
            # User is neither authorized for other accounts nor has his own
            # account -> redirect to account setup
            return redirect("account_setup")
        except AttributeError:
            # No user on request 
            raise ImproperlyConfigured(
                "%s needs django's 'AuthenticationMiddleware' to be enabled."
            )

