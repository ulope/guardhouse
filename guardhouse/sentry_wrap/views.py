from django.http import HttpResponseNotAllowed, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from sentry_wrap.tasks import input_message

@csrf_exempt
def store(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed('This method only supports POST requests')
    input_message.delay(
        request.POST.get('data'), request.POST.get('format', 'pickle'),
        request.POST.get('key'), request.META.get('HTTP_AUTHORIZATION', ''),
        request.raw_post_data
    )

    return HttpResponse()
