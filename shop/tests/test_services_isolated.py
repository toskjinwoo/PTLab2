"""Изолированные unit-тесты make_purchase: зависимости подменены моками."""
from unittest import mock

from django.test import TestCase
from shop.models import Customer, Product
from shop import services


class MakePurchaseIsolatedTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Пылесос", price=12000)

    @mock.patch('shop.services.apply_discount', return_value=1)
    def test_price_paid_comes_from_apply_discount(self, apply_mock):
        purchase = services.make_purchase(self.product, "Иванов", "a")
        apply_mock.assert_called_once_with(12000, 0)
        self.assertEqual(purchase.price_paid, 1)
        self.assertEqual(Customer.objects.get(name="Иванов").total_spent, 1)

    @mock.patch('shop.models.get_discount_percent', return_value=15)
    def test_discount_percent_comes_from_discount_rules(self, rules_mock):
        purchase = services.make_purchase(self.product, "Иванов", "a")
        rules_mock.assert_called_once_with(0)
        self.assertEqual(purchase.discount_percent, 15)
        self.assertEqual(purchase.price_paid, 10200)

    @mock.patch('shop.services.Purchase.objects.create',
                side_effect=RuntimeError('db failure'))
    def test_failure_rolls_back_whole_purchase(self, _):
        with self.assertRaises(RuntimeError):
            services.make_purchase(self.product, "Иванов", "a")
        # транзакция откатилась: покупатель не остался в базе
        self.assertFalse(Customer.objects.filter(name="Иванов").exists())
