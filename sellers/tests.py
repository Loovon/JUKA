# sellers/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from sellers.models import SellerProfile, Shop

User = get_user_model()

class SellerProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="seller1",
            password="pass123"
        )

    def test_seller_profile_created(self):
        profile = SellerProfile.objects.create(
            user=self.user,
            store_name="JUKA Store"
        )
        self.assertEqual(profile.store_name, "JUKA Store")
        self.assertFalse(profile.verified)

    def test_str_representation(self):
        profile = SellerProfile.objects.create(
            user=self.user,
            store_name="My Shop"
        )
        self.assertEqual(str(profile), "Seller: My Shop")


class ShopModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="seller2",
            password="pass123"
        )

    def test_shop_creation_defaults(self):
        shop = Shop.objects.create(
            seller=self.user,
            shop_name="JUKA Main Shop"
        )
        self.assertTrue(shop.active)
        self.assertEqual(shop.rank, "hustler")

    def test_one_shop_per_seller(self):
        Shop.objects.create(
            seller=self.user,
            shop_name="Shop One"
        )
        with self.assertRaises(Exception):
            Shop.objects.create(
                seller=self.user,
                shop_name="Shop Two"
            )

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from sellers.models import Shop, Advert, AdvertVariant, ShopImage
from categories.models import Category

User = get_user_model()


class AdvertModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="seller",
            password="pass123",
            role="seller"
        )

        self.category = Category.objects.create(name="Electronics")

        self.shop = Shop.objects.create(
            seller=self.user,
            shop_name="JUKA Shop"
        )

        self.image = SimpleUploadedFile(
            name="test.jpg",
            content=b"file_content",
            content_type="image/jpeg"
        )

    def test_advert_creation(self):
        advert = Advert.objects.create(
            shop=self.shop,
            seller=self.user,
            title="Phone",
            category=self.category,
            price=10000,
            image=self.image
        )

        self.assertEqual(advert.title, "Phone")
        self.assertEqual(advert.shop, self.shop)
        self.assertTrue(advert.active)

    def test_advert_deleted_with_shop(self):
        advert = Advert.objects.create(
            shop=self.shop,
            seller=self.user,
            title="TV",
            category=self.category,
            price=50000,
            image=self.image
        )
        self.shop.delete()
        self.assertEqual(Advert.objects.count(), 0)


class AdvertVariantTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="seller2", password="pass")
        self.category = Category.objects.create(name="Furniture")
        self.shop = Shop.objects.create(seller=self.user, shop_name="FurniShop")

        self.advert = Advert.objects.create(
            shop=self.shop,
            seller=self.user,
            title="Table",
            category=self.category,
            price=2000,
            image=SimpleUploadedFile("a.jpg", b"img")
        )

    def test_variant_creation(self):
        variant = AdvertVariant.objects.create(
            advert=self.advert,
            color="Brown",
            type="Wood"
        )

        self.assertEqual(str(variant), "Variant of Table")


class ShopImageTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="seller3", password="pass")
        self.shop = Shop.objects.create(seller=self.user, shop_name="ImageShop")

    def test_shop_image_upload(self):
        image = ShopImage.objects.create(
            shop=self.shop,
            image=SimpleUploadedFile("logo.jpg", b"img")
        )

        self.assertEqual(image.shop, self.shop)
