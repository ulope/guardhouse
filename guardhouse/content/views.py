from django.contrib.sites.models import Site
from django.shortcuts import render
from django.views.generic.simple import direct_to_template

def home(request):
    site = Site.objects.get_current()
    return render(request, "content/home.html", {'site': site})

def impressum(request):
    return direct_to_template(request, "content/impressum.html")
