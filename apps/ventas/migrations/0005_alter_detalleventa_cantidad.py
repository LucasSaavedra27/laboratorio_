# Generated by Django 4.2 on 2024-10-25 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0004_delete_facturaafip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detalleventa',
            name='cantidad',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]