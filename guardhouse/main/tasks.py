from celery.decorators import task
from dns import rdatatype, rdtypes
from dns.resolver import Resolver, NXDOMAIN
import requests

url_templates = [
    "http://%s/",
    "https://%s/",
    "http://www.%s/",
    "https://www.%s/",
]

@task(retries=4)
def verify_site(site_id):
    """Celery task to verify site ownership"""

    from .models import Site
    site = Site.objects.get(pk=site_id)
    key = site.get_verification_key()

    valid = False

    # Check header and content for the verification key in some common URL
    # variations
    for url in url_templates:
        resp = requests.get(url % site.domain, timeout=3)
        if not resp.ok:
            continue
        valid = valid or key in resp.headers.get("X-Guardhouse-Verify", "")
        valid = valid or key in resp.content
        if valid:
            break

    if not valid:
        # Still not valid - check DNS
        resolver = Resolver()
        try:
            result = resolver.query("%s.%s." % (key, site.domain), rdatatype.CNAME)
            try:
                for answer in result.response.answer:
                    for item in answer.items:
                        if (isinstance(item, rdtypes.ANY.CNAME.CNAME) and
                            item.target.to_text() == "verify.guardhous.es"):
                            valid = True
                            raise StopIteration()
            except StopIteration:
                pass
        except NXDOMAIN:
            # Domain doesn't exist - nothing we can do
            pass
            
    if valid:
        site.verified = True
        site.save()
        return True
    # Fall trough - retry
    verify_site.retry(countdown=10)
