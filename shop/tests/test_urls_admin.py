from django.contrib import admin
from django.test import SimpleTestCase
from django.urls import resolve, reverse
from shop import views
from shop.models import Customer, Product, Purchase


class UrlsTestCase(SimpleTestCase):
    def test_reverse(self):
        self.assertEqual(reverse('index'), '/')
        self.assertEqual(reverse('buy', args=[3]), '/buy/3/')
        self.assertEqual(reverse('customers'), '/customers/')

    def test_resolve(self):
        self.assertEqual(resolve('/').func, views.index)
        self.assertEqual(resolve('/customers/').func, views.customers)
        self.assertEqual(resolve('/buy/3/').func.view_class,
                         views.PurchaseCreate)

    def test_buy_requires_integer_id(self):
        with self.assertRaises(Exception):
            resolve('/buy/abc/')


class AdminTestCase(SimpleTestCase):
    def test_models_are_registered(self):
        for model in (Product, Customer, Purchase):
            self.assertTrue(admin.site.is_registered(model), model)
