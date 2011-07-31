from django.db import models

class SiteMessage(models.Model):
    site = models.ForeignKey("main.Site", related_name="sentry_messages")
    message = models.ForeignKey("sentry.Message", related_name="guardhouse_site")

    def __unicode__(self):
        return u"Message for site '%s'" % (self.site.name,)
