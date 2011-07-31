from celery.decorators import task
from dns import rdatatype, rdtypes
from dns.resolver import Resolver, NXDOMAIN
import requests

url_templates = [
    "http://%(domain)s/",
    "https://%(domain)s/",
    "http://www.%(domain)s/",
    "https://www.%(domain)s/",
    "http://%(domain)s/%(key)s",
    "https://%(domain)s/%(key)s",
    "http://www.%(domain)s/%(key)s",
    "https://www.%(domain)s/%(key)s",
]

@task(retries=4)
def verify_site(site_id, retry_count=1):
    """Celery task to verify site ownership"""

    from .models import Site
    site = Site.objects.get(pk=site_id)
    key = site.get_verification_key()

    valid = False

    # Check header, content and files for the verification key in some common
    # URL variations
    for url_template in url_templates:
        url = url_template % {'domain': site.domain, 'key': key}
        resp = requests.get(url, timeout=3)
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
                            "verify.guardhous.es" in item.target.to_text()):
                            valid = True
                            raise StopIteration()
            except StopIteration:
                pass
        except NXDOMAIN:
            # Domain doesn't exist - nothing we can do
            pass
            
    from .models import VERIFY_STATE
    if valid:
        site.verification_state = VERIFY_STATE.VERIFIED
        site.save()
        return True
    if retry_count >= 4:
        # We already tried 3 times - time to give up
        site.verification_state = VERIFY_STATE.FAILED
        site.save()
    # Fall trough - retry
    verify_site.retry(countdown=10, args=(site_id, retry_count + 1))
