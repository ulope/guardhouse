guardhouse

This project was cerated as part of the djangodash 2011 (http://djangodash.com)

The purpose of this project is to offer a centralized collection place for 
django-sentry (https://github.com/dcramer/django-sentry) exception logs.

Currently working functionality:
* User creation / login (via django-social-auth)
* Ceration of Sites (domains from which logs are accepted) incl. async 
  verification of domain ownership
* Reception of sentry exception logs

Baerly working functionality:
* Displaying of exception logs - The plan is to integrate sentry's views


The requirements are listed in pip freeze format in req.txt

Configuration requirement:
A django "secret key" must be placed in a file called ".secret" in the django
project root.
For Twitter OAuth to be working TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET
need to be defined (e.g. in local_settings.py).

A working instance can be found at http://guardhous.es/

(For the djangodash judges: http://guardhouse.ep.io)
