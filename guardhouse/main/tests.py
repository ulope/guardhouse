from celery.exceptions import RetryTaskError
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
from django.utils.unittest import skipUnless
from mock import patch
from .tasks import verify_site
from .models import Account, Site


class MockRequestsGet(object):
    """Mock replacement for 'requests'"""
    def __init__(self, key):
        self.key = key

    def __call__(self, *args, **kwargs):
        class MockResult(object):
            ok = True
            headers = {'X-Guardhouse-Verify': self.key}
            #noinspection PyMethodParameters
            def read(me):
                return self.key
        return MockResult()

class MainTest(TransactionTestCase):
    def setUp(self):
        self.user_wo_account = User.objects.create_user(
            username="test1", password="test", email="a@b.com"
        )
        self.user_w_account = User.objects.create_user(
            username="test2", password="test", email="a@b.com"
        )
        self.user_w_access_perm = User.objects.create_user(
            username="test3", password="test", email="a@b.com"
        )
        account = Account.objects.create(name="Test account",
                                         owner=self.user_w_account)
        account.delegates.add(self.user_w_access_perm)
        self.site1 = Site.objects.create(
            name="Verified site", domain="example.com", verified=True,
            belongs_to=account
        )
        self.site2 = Site.objects.create(
            name="Unverified site", domain="example.com", belongs_to=account
        )


    @skipUnless("main.middleware.HasAccountMiddleware" in settings.MIDDLEWARE_CLASSES,
                "'HasAccountMiddleware' isn't installed")
    def test_has_account_middleware(self):
        """
        Test if users wihtout account or access to other accounts are redirected
        to the account setup.
        """
        self.client.login(username="test1", password="test")
        self.assertRedirects(self.client.get("/"), "account/setup/")
        self.client.logout()

        self.client.login(username="test2", password="test")
        self.assertEquals(200, self.client.get("/").status_code)
        self.client.logout()

        self.client.login(username="test3", password="test")
        self.assertEquals(200, self.client.get("/").status_code)
        self.client.logout()

    def test_verify_site(self):
        """
        Test site ownership verification
        """
        self.assertRaises(RetryTaskError, verify_site, self.site2.pk)

        with patch(
            "main.tasks.requests.get",
            MockRequestsGet(self.site2.get_verification_key())):
            self.assertEquals(verify_site.delay(self.site2.pk).result, True)
            # Reload from DB
            self.site2 = Site.objects.get(pk=self.site2.pk)
            self.assertEqual(self.site2.verified, True)
            