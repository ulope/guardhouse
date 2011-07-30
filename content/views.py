# Create your views here.
from django.views.generic.simple import direct_to_template

def home(request):
    return direct_to_template(request, "content/home.html")

def impressum(request):
    return direct_to_template(request, "content/impressum.html")
