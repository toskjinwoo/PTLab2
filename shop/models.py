from django.db import models

from .discounts import get_discount_percent


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Customer(models.Model):
    """Покупатель. Учитывается общая сумма его покупок."""
    name = models.CharField(max_length=200, unique=True)
    total_spent = models.PositiveIntegerField(default=0)

    @property
    def discount_percent(self) -> int:
        return get_discount_percent(self.total_spent)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    # Фактически уплаченная сумма и скидка, действовавшая на момент покупки
    price_paid = models.PositiveIntegerField(default=0)
    discount_percent = models.PositiveSmallIntegerField(default=0)
