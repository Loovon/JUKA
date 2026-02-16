from django.test import TestCase
from categories.models import Category


class CategoryModelTest(TestCase):

    def test_slug_auto_generation(self):
        cat = Category.objects.create(name="Home Appliances")
        self.assertEqual(cat.slug, "home-appliances")

    def test_slug_uniqueness(self):
        Category.objects.create(name="Electronics")
        cat2 = Category.objects.create(name="Electronics")

        self.assertEqual(cat2.slug, "electronics-1")
