from django.db import transaction

from .discounts import apply_discount
from .models import Customer, Product, Purchase


@transaction.atomic
def make_purchase(product: Product, person: str, address: str) -> Purchase:
    """Оформляет покупку с учетом накопительной скидки покупателя.

    Скидка определяется по сумме ПРЕДЫДУЩИХ покупок. После покупки
    уплаченная сумма добавляется к накопленной.
    """
    customer, _ = Customer.objects.get_or_create(name=person)
    # блокировка строки, чтобы параллельные покупки не потеряли сумму
    customer = Customer.objects.select_for_update().get(pk=customer.pk)

    percent = customer.discount_percent
    price_paid = apply_discount(product.price, percent)
    purchase = Purchase.objects.create(
        product=product, customer=customer, address=address,
        price_paid=price_paid, discount_percent=percent)

    customer.total_spent += price_paid
    customer.save(update_fields=['total_spent'])
    return purchase
