from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class PersonToCustomerMigrationTestCase(TransactionTestCase):
    """Проверка переноса строкового person в таблицу покупателей."""
    before = [('shop', '0001_initial')]
    after = [('shop', '0003_remove_purchase_person')]

    def migrate(self, target):
        executor = MigrationExecutor(connection)
        executor.migrate(target)
        executor.loader.build_graph()
        return executor.loader.project_state(target).apps

    def setUp(self):
        old_apps = self.migrate(self.before)
        Product = old_apps.get_model('shop', 'Product')
        Purchase = old_apps.get_model('shop', 'Purchase')
        table = Product.objects.create(name='Стол', price=2000)
        chair = Product.objects.create(name='Стул', price=1000)
        Purchase.objects.create(product=table, person='Иванов', address='a')
        Purchase.objects.create(product=chair, person='Иванов', address='b')
        Purchase.objects.create(product=chair, person='Петров', address='c')

    def tearDown(self):
        self.migrate([n for n in MigrationExecutor(
            connection).loader.graph.leaf_nodes()])

    def test_customers_are_created_with_total(self):
        new_apps = self.migrate(self.after)
        Customer = new_apps.get_model('shop', 'Customer')
        totals = {c.name: c.total_spent for c in Customer.objects.all()}
        self.assertEqual(totals, {'Иванов': 3000, 'Петров': 1000})

    def test_purchases_are_linked_to_customers(self):
        new_apps = self.migrate(self.after)
        Purchase = new_apps.get_model('shop', 'Purchase')
        for purchase in Purchase.objects.all():
            self.assertEqual(purchase.price_paid, purchase.product.price)
            self.assertEqual(purchase.discount_percent, 0)
        self.assertEqual(Purchase.objects.filter(
            customer__name='Иванов').count(), 2)
