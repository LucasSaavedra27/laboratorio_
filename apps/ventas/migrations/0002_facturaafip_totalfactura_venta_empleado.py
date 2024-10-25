# Generated by Django 4.2 on 2024-10-16 15:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
        ('ventas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='facturaafip',
            name='totalFactura',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='venta',
            name='empleado',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ventaEmpleado', to='usuarios.empleado'),
            preserve_default=False,
        ),
    ]