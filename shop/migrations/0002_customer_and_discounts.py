from django.db import migrations, models
import django.db.models.deletion


def person_to_customer(apps, schema_editor):
    """Переносит строковое поле person в таблицу покупателей."""
    Customer = apps.get_model('shop', 'Customer')
    Purchase = apps.get_model('shop', 'Purchase')
    for purchase in Purchase.objects.select_related('product'):
        customer, _ = Customer.objects.get_or_create(name=purchase.person)
        purchase.customer = customer
        purchase.price_paid = purchase.product.price
        purchase.save(update_fields=['customer', 'price_paid'])
        customer.total_spent += purchase.price_paid
        customer.save(update_fields=['total_spent'])


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('total_spent', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='purchase',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.customer'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='price_paid',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='purchase',
            name='discount_percent',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.RunPython(person_to_customer, migrations.RunPython.noop),
    ]
