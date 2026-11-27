from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_customer_and_discounts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='person',
        ),
        migrations.AlterField(
            model_name='purchase',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.customer'),
        ),
    ]
