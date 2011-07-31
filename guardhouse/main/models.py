from django.db import models
from django.utils.translation import ugettext as _

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

class Site(BaseModel):
    """
    A site for which messages are accepted. Has to be verified before it can be
    used.
    """
    name = models.CharField(_("Name"), max_length=300)
    domain = models.CharField(_("Domain name"), max_length=300)
    allow_wild_subdomain = models.BooleanField(
        _("Allow wildcard subdomains"), default=False,
        help_text=_("Check this to also accept messages for all subdomains.")
    )
    belongs_to = models.ForeignKey(Account, verbose_name=_("Account"),
                                   related_name="sites")
    verified = models.BooleanField(_("Verified"), default=False)

    class Meta(object):
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        ordering = ("name",)

    def __unicode__(self):
        if self.verified:
            return self.name
        return _(u"%s [not verified]") % self.name


