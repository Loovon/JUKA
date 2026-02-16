from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserTest(TestCase):

    def test_default_role_is_buyer(self):
        user = User.objects.create_user(username="buyer", password="pass")
        self.assertTrue(user.is_buyer)
        self.assertFalse(user.is_seller)

    def test_seller_role(self):
        user = User.objects.create_user(
            username="seller",
            password="pass",
            role="seller"
        )
        self.assertTrue(user.is_seller)
