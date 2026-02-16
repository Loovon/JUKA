from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from sellers.models import SellerProfile, Shop, Advert
from categories.models import Category

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


User = get_user_model()


class JukaIntegrationTest(TestCase):
    """
    Stable integration tests for JUKA.
    Focus: database outcomes, not view internals or templates.
    """

    def setUp(self):
        self.client = Client()

        # -------------------------
        # User
        # -------------------------
        self.user = User.objects.create_user(
            username="seller1",
            password="pass1234",
        )
        self.user.role = "seller"
        self.user.save()

        self.client.login(username="seller1", password="pass1234")

        # -------------------------
        # Seller profile
        # -------------------------
        self.seller_profile = SellerProfile.objects.create(
            user=self.user,
            store_name="Test Store",
            phone_number="123456789"
        )

        # -------------------------
        # Shop
        # -------------------------
        self.shop = Shop.objects.create(
            seller=self.user,
            shop_name="My Shop",
            phone="123456789"
        )

        # -------------------------
        # Category
        # -------------------------
        self.category = Category.objects.create(
            name="Construction"
        )

        # -------------------------
        # SocialApp (allauth safety)
        # -------------------------
        site = Site.objects.get_current()
        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="dummy",
            secret="dummy"
        )
        app.sites.add(site)

    # ==================================================
    # HAPPY PATH (MODEL-LEVEL INTEGRATION)
    # ==================================================
    def test_full_seller_flow_creates_advert(self):
        advert = Advert.objects.create(
            shop=self.shop,
            seller=self.user,
            title="Premium Cement",
            category=self.category,
            price=100
        )

        self.assertEqual(Advert.objects.count(), 1)
        self.assertEqual(advert.shop, self.shop)
        self.assertEqual(advert.seller, self.user)
        self.assertEqual(advert.price, 100)

    # ==================================================
    # INVALID PRICE
    # ==================================================
    # ==================================================
    # NEGATIVE PRICE (MODEL ALLOWS IT)
    # ==================================================
    def test_negative_price_is_saved_at_model_level(self):
        advert = Advert.objects.create(
            shop=self.shop,
            seller=self.user,
            title="Negative Price",
            category=self.category,
            price=-50
        )

        self.assertEqual(Advert.objects.count(), 1)
        self.assertEqual(advert.price, -50)

    # ==================================================
    # INVALID IMAGE (VIEW SAFETY)
    # ==================================================
    def test_invalid_image_upload_does_not_create_advert(self):
        invalid_file = SimpleUploadedFile(
            "file.txt",
            b"hello world",
            content_type="text/plain"
        )

        self.client.post(
            reverse("create_advert"),
            {
                "title": "Invalid Image",
                "category": self.category.id,
                "price": 100,
                "image": invalid_file,
            },
            follow=True
        )

        self.assertEqual(Advert.objects.count(), 0)

    # ==================================================
    # LARGE FILE
    # ==================================================
    def test_large_file_upload_does_not_create_advert(self):
        large_image = SimpleUploadedFile(
            "large.jpg",
            b"a" * 50_000_000,
            content_type="image/jpeg"
        )

        self.client.post(
            reverse("create_advert"),
            {
                "title": "Large File",
                "category": self.category.id,
                "price": 100,
                "image": large_image,
            },
            follow=True
        )

        self.assertEqual(Advert.objects.count(), 0)

    # ==================================================
    # DUPLICATE USER (ALLAUTH SAFE)
    # ==================================================
    def test_duplicate_user_signup_does_not_create_account(self):
        User.objects.create_user(
            username="duplicate",
            password="1234pass"
        )

        initial_count = User.objects.count()

        self.client.post(
            reverse("account_signup"),
            {
                "username": "duplicate",
                "password1": "1234pass",
                "password2": "1234pass",
            },
            follow=True
        )

        self.assertEqual(User.objects.count(), initial_count)





# existing imports stay
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from sellers.models import SellerProfile, Shop
from categories.models import Category

User = get_user_model()


class JukaUITemplateTest(TestCase):
    """
    UI-level tests.
    Focus: templates render without error (no browser, no Selenium).
    """

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="uiuser",
            password="pass1234"
        )
        self.user.role = "seller"
        self.user.save()

        self.client.login(username="uiuser", password="pass1234")

        self.profile = SellerProfile.objects.create(
            user=self.user,
            store_name="UI Store",
            phone_number="123456789"
        )

        self.shop = Shop.objects.create(
            seller=self.user,
            shop_name="UI Shop",
            phone="123456789"
        )

        self.category = Category.objects.create(name="Construction")

        # --- Add SocialApp to prevent template errors ---
        site = Site.objects.get_current()
        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="dummy",
            secret="dummy"
        )
        app.sites.add(site)

    def test_home_page_renders(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_create_advert_page_renders(self):
        response = self.client.get(reverse("create_advert"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_advert.html")

    def test_my_shop_page_renders(self):
        response = self.client.get(
            reverse("my_shop", args=[self.profile.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "my_shop.html")

    def test_my_adverts_page_renders(self):
        response = self.client.get(reverse("my_adverts"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "my_adverts.html")
