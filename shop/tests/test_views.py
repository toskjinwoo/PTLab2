from django.test import TestCase, Client
from shop.models import Customer, Product, Purchase


class IndexTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        Product.objects.create(name="Холодильник", price=45000)

    def test_webpage_accessibility(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_products_and_discount_tiers_are_shown(self):
        response = self.client.get('/')
        self.assertContains(response, "Холодильник")
        self.assertContains(response, "45000")
        self.assertContains(response, "10000")
        self.assertContains(response, "15%")


class PurchaseCreateTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(name="Стиральная машина",
                                              price=10000)
        self.url = f'/buy/{self.product.id}/'

    def buy(self, person="Иванов", address="Светлая ул."):
        return self.client.post(self.url, {
            'product': self.product.id,
            'person': person,
            'address': address})

    def test_form_page_accessibility(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Стиральная машина")

    def test_form_page_of_missing_product(self):
        self.assertEqual(self.client.get('/buy/999/').status_code, 404)

    def test_successful_purchase(self):
        response = self.buy()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Спасибо за покупку, Иванов!")
        self.assertEqual(Purchase.objects.count(), 1)
        self.assertEqual(Customer.objects.get(name="Иванов").total_spent,
                         10000)

    def test_second_purchase_shows_discount(self):
        self.buy()
        response = self.buy()
        self.assertContains(response, "Ваша скидка: 3%")
        self.assertContains(response, "9700")
        self.assertEqual(Customer.objects.get(name="Иванов").total_spent,
                         19700)

    def test_empty_name_is_rejected(self):
        response = self.buy(person="   ")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Purchase.objects.count(), 0)
        self.assertEqual(Customer.objects.count(), 0)

    def test_empty_address_is_rejected(self):
        response = self.buy(address="")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Purchase.objects.count(), 0)

    def test_unknown_product_is_rejected(self):
        response = self.client.post(self.url, {
            'product': 999, 'person': 'Иванов', 'address': 'a'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Purchase.objects.count(), 0)


class CustomersTestCase(TestCase):
    def test_empty_list(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Покупателей пока нет")

    def test_customers_sorted_by_total_spent(self):
        Customer.objects.create(name="Бедный", total_spent=100)
        Customer.objects.create(name="Богатый", total_spent=60000)
        response = self.client.get('/customers/')
        content = response.content.decode()
        self.assertLess(content.index("Богатый"), content.index("Бедный"))
        self.assertContains(response, "10%")


class EmptyShopTestCase(TestCase):
    def test_index_without_products(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 0)

    def test_unknown_url(self):
        self.assertEqual(self.client.get('/nothing/').status_code, 404)

    def test_get_does_not_create_purchase(self):
        product = Product.objects.create(name="Чайник", price=2500)
        self.client.get(f'/buy/{product.id}/')
        self.assertEqual(Purchase.objects.count(), 0)


class FullScenarioTestCase(TestCase):
    """Сквозной сценарий: покупатель набирает скидку."""

    def test_discount_grows_with_purchases(self):
        product = Product.objects.create(name="Холодильник", price=45000)
        url = f'/buy/{product.id}/'
        data = {'product': product.id, 'person': 'Иванов', 'address': 'a'}
        self.assertContains(self.client.post(url, data), "К оплате: <b>45000")
        # потрачено 45000 -> скидка 5%
        self.assertContains(self.client.post(url, data), "К оплате: <b>42750")
        # потрачено 87750 -> скидка 10%
        self.assertContains(self.client.post(url, data), "К оплате: <b>40500")
        self.assertEqual(Customer.objects.get(name='Иванов').total_spent,
                         128250)
