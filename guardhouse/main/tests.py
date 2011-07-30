from django.conf import settings
from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.utils.unittest import skipUnless
from .models import Account, Site


class MiddlewareTest(TransactionTestCase):
    def setUp(self):
        site = Site.objects.create(name="Test site", domain="example.com",
                                   verified=True)
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
        account.sites.add(site)

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
        