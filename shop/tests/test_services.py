from django.test import TestCase
from shop.models import Customer, Product, Purchase
from shop.services import make_purchase


class MakePurchaseTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="washer", price=10000)
        self.cheap = Product.objects.create(name="kettle", price=2500)

    def test_first_purchase_has_no_discount(self):
        purchase = make_purchase(self.product, "Ivanov", "Svetlaya St.")
        self.assertEqual(purchase.discount_percent, 0)
        self.assertEqual(purchase.price_paid, 10000)
        self.assertEqual(purchase.address, "Svetlaya St.")

    def test_customer_is_created(self):
        make_purchase(self.product, "Ivanov", "Svetlaya St.")
        customer = Customer.objects.get(name="Ivanov")
        self.assertEqual(customer.total_spent, 10000)

    def test_existing_customer_is_reused(self):
        make_purchase(self.cheap, "Ivanov", "Svetlaya St.")
        make_purchase(self.cheap, "Ivanov", "Svetlaya St.")
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Purchase.objects.count(), 2)

    def test_different_customers_are_independent(self):
        make_purchase(self.product, "Ivanov", "a")
        purchase = make_purchase(self.product, "Petrov", "b")
        self.assertEqual(purchase.discount_percent, 0)
        self.assertEqual(Customer.objects.count(), 2)

    def test_discount_after_reaching_threshold(self):
        make_purchase(self.product, "Ivanov", "a")  # потрачено 10000
        second = make_purchase(self.product, "Ivanov", "a")
        self.assertEqual(second.discount_percent, 3)
        self.assertEqual(second.price_paid, 9700)

    def test_discount_is_based_on_amount_actually_paid(self):
        # 10000 + 9700 + 9700 = 29400 < 30000, значит, 4-я покупка
        # все еще со скидкой 3%, а не 5%
        for _ in range(3):
            make_purchase(self.product, "Ivanov", "a")
        self.assertEqual(Customer.objects.get(name="Ivanov").total_spent,
                         29400)
        fourth = make_purchase(self.product, "Ivanov", "a")
        self.assertEqual(fourth.discount_percent, 3)
        fifth = make_purchase(self.product, "Ivanov", "a")
        self.assertEqual(fifth.discount_percent, 5)

    def test_discount_does_not_apply_to_current_purchase_itself(self):
        big = Product.objects.create(name="fridge", price=100000)
        purchase = make_purchase(big, "Ivanov", "a")
        self.assertEqual(purchase.discount_percent, 0)
        self.assertEqual(purchase.price_paid, 100000)
        self.assertEqual(Customer.objects.get(name="Ivanov").discount_percent,
                         15)

    def test_history_keeps_discount_of_each_purchase(self):
        make_purchase(self.product, "Ivanov", "a")
        make_purchase(self.product, "Ivanov", "a")
        discounts = list(Purchase.objects.order_by("id")
                         .values_list("discount_percent", flat=True))
        self.assertEqual(discounts, [0, 3])

    def test_free_product(self):
        free = Product.objects.create(name="gift", price=0)
        purchase = make_purchase(free, "Ivanov", "a")
        self.assertEqual(purchase.price_paid, 0)
        self.assertEqual(Customer.objects.get(name="Ivanov").total_spent, 0)

    def test_customer_names_are_case_sensitive(self):
        make_purchase(self.cheap, "Ivanov", "a")
        make_purchase(self.cheap, "ivanov", "a")
        self.assertEqual(Customer.objects.count(), 2)
