from django.conf import settings

def google_analytics(request):
    try:
        return {
            'GOOGLE_ANALYTICS_DOMAIN': settings.GOOGLE_ANALYTICS_DOMAIN,
            'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID
        }
    except AttributeError:
        pass
