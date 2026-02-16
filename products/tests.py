from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from products.models import Product
from categories.models import Category


class ProductModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Construction")

    def test_product_creation(self):
        product = Product.objects.create(
            category=self.category,
            name="Cement",
            price=750,
            image=SimpleUploadedFile("cement.jpg", b"img")
        )

        self.assertEqual(product.name, "Cement")
        self.assertEqual(product.category.name, "Construction")

    def test_product_str(self):
        product = Product.objects.create(
            category=self.category,
            name="Bricks",
            price=50,
            image=SimpleUploadedFile("bricks.jpg", b"img")
        )
        self.assertEqual(str(product), "Bricks")
