# Generated by Django 4.2 on 2024-10-30 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0002_producto_unidaddemedida'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='cantidadDisponible',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
