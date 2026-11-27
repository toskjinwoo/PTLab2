from django.db import IntegrityError, transaction
from django.test import TestCase
from shop.models import Customer, Product, Purchase
from datetime import datetime


class ProductTestCase(TestCase):
    def setUp(self):
        Product.objects.create(name="fridge", price="740")
        Product.objects.create(name="kettle", price="50")

    def test_correctness_types(self):
        self.assertIsInstance(Product.objects.get(name="fridge").name, str)
        self.assertIsInstance(Product.objects.get(name="fridge").price, int)
        self.assertIsInstance(Product.objects.get(name="kettle").name, str)
        self.assertIsInstance(Product.objects.get(name="kettle").price, int)

    def test_correctness_data(self):
        self.assertTrue(Product.objects.get(name="fridge").price == 740)
        self.assertTrue(Product.objects.get(name="kettle").price == 50)

    def test_str(self):
        self.assertEqual(str(Product.objects.get(name="kettle")), "kettle")


class CustomerTestCase(TestCase):
    def test_defaults(self):
        customer = Customer.objects.create(name="Ivanov")
        self.assertEqual(customer.total_spent, 0)
        self.assertEqual(customer.discount_percent, 0)

    def test_discount_percent_depends_on_total_spent(self):
        customer = Customer.objects.create(name="Ivanov", total_spent=30000)
        self.assertEqual(customer.discount_percent, 5)

    def test_name_is_unique(self):
        Customer.objects.create(name="Ivanov")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Customer.objects.create(name="Ivanov")

    def test_name_field_declaration(self):
        field = Customer._meta.get_field('name')
        self.assertTrue(field.unique)
        self.assertEqual(field.max_length, 200)

    def test_str(self):
        self.assertEqual(str(Customer(name="Ivanov")), "Ivanov")


class PurchaseTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="fridge", price="740")
        self.customer = Customer.objects.create(name="Ivanov")
        self.datetime = datetime.now()
        Purchase.objects.create(product=self.product,
                                customer=self.customer,
                                address="Svetlaya St.")

    def test_correctness_types(self):
        purchase = Purchase.objects.get(product=self.product)
        self.assertIsInstance(purchase.customer.name, str)
        self.assertIsInstance(purchase.address, str)
        self.assertIsInstance(purchase.date, datetime)
        self.assertIsInstance(purchase.price_paid, int)
        self.assertIsInstance(purchase.discount_percent, int)

    def test_correctness_data(self):
        purchase = Purchase.objects.get(product=self.product)
        self.assertTrue(purchase.customer.name == "Ivanov")
        self.assertTrue(purchase.address == "Svetlaya St.")
        self.assertTrue(purchase.date.replace(microsecond=0) ==
                        self.datetime.replace(microsecond=0))

    def test_default_discount_fields(self):
        purchase = Purchase.objects.get(product=self.product)
        self.assertEqual(purchase.price_paid, 0)
        self.assertEqual(purchase.discount_percent, 0)
