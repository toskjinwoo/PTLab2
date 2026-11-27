from django.test import TestCase
from shop.forms import PurchaseForm
from shop.models import Product


class PurchaseFormTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Чайник", price=2500)

    def data(self, **changes):
        data = {'product': self.product.id, 'person': 'Иванов',
                'address': 'Светлая ул.'}
        data.update(changes)
        return data

    def test_valid_form(self):
        form = PurchaseForm(self.data())
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['product'], self.product)

    def test_name_is_stripped(self):
        form = PurchaseForm(self.data(person='  Иванов  '))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['person'], 'Иванов')

    def test_required_fields(self):
        for field in ('product', 'person', 'address'):
            data = self.data()
            del data[field]
            form = PurchaseForm(data)
            self.assertFalse(form.is_valid(), field)
            self.assertIn(field, form.errors)

    def test_blank_name_is_invalid(self):
        self.assertFalse(PurchaseForm(self.data(person='   ')).is_valid())

    def test_too_long_name_is_invalid(self):
        form = PurchaseForm(self.data(person='И' * 201))
        self.assertFalse(form.is_valid())

    def test_max_length_name_is_valid(self):
        self.assertTrue(PurchaseForm(self.data(person='И' * 200)).is_valid())

    def test_unknown_product_is_invalid(self):
        form = PurchaseForm(self.data(product=999))
        self.assertFalse(form.is_valid())
        self.assertIn('product', form.errors)
