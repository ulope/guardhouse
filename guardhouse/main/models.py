import hmac
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from main.util import VerifyRun
from .tasks import verify_site

class BaseModel(models.Model):
    """Abstract base model"""
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Last modified"), auto_now=True)

    class Meta(object):
        abstract = True

class Account(BaseModel):
    """
    An account defines sites and users that are allowed to access error messages
    for them.
    """
    name = models.CharField(_("Name"), max_length=300)
    owner = models.OneToOneField(
        "auth.User", verbose_name=_("Account Owner"), related_name="account"
    )
    delegates = models.ManyToManyField(
        "auth.User", verbose_name=_("Authorized users"), null=True, blank=True,
        related_name="authorized_for",
        
    )

    class Meta(object):
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        ordering = ("name",)

    def __unicode__(self):
        return self.name

class VERIFY_STATE(object):
    NEW = "new"
    VERIFYING = "verifying"
    FAILED = "failed"
    VERIFIED = "verified"

VERIFICATION_STATE_CHOICES = (
    (VERIFY_STATE.NEW, _("New")),
    (VERIFY_STATE.VERIFYING, _("Verifying...")),
    (VERIFY_STATE.FAILED, _("Failed")),
    (VERIFY_STATE.VERIFIED, _("Verified")),
)

class Site(BaseModel):
    """
    A site for which messages are accepted. Has to be verified before it can be
    used.
    """
    name = models.CharField(_("Name"), max_length=300)
    domain = models.CharField(_("Domain name"), max_length=300, unique=True)
    allow_wild_subdomain = models.BooleanField(
        _("Allow wildcard subdomains"), default=False,
        help_text=_("Check this to also accept messages for all subdomains.")
    )
    belongs_to = models.ForeignKey(Account, verbose_name=_("Account"),
                                   related_name="sites")
    verification_state = models.CharField(
        _("Verified"), default=VERIFY_STATE.NEW,
        choices=VERIFICATION_STATE_CHOICES, max_length=10
    )

    class Meta(object):
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        ordering = ("name",)

    def __unicode__(self):
        if self.verified:
            return self.name
        return _(u"%s [not verified]") % self.name

    def get_verification_key(self):
        """Returns a hexdigest of an hmac calculated from the domain name"""
        return hmac.new(settings.SECRET_KEY, self.domain).hexdigest()

    @property
    def verified(self):
        return self.verification_state == VERIFY_STATE.VERIFIED

    @property
    def verifying(self):
        return self.verification_state == VERIFY_STATE.VERIFYING

    def verify(self, request=False):
        """
        Dispatch verification job to celery and (if request is given) add
        a VerifyRun object to the session.
        """
        self.verification_state = VERIFY_STATE.VERIFYING
        self.save()
        task = verify_site.delay(self.pk)
        request.session.setdefault('verify_runs', []).append(
            VerifyRun(task, self.pk)
        )
        return task
