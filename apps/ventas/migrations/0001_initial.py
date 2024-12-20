# Generated by Django 4.2 on 2024-10-16 15:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClienteMayorista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=50)),
                ('direccion', models.CharField(max_length=50)),
                ('telefono', models.CharField(max_length=15)),
                ('mail', models.EmailField(blank=True, max_length=254, null=True)),
                ('cuil', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechaDeVenta', models.DateTimeField()),
                ('formaDePago', models.CharField(choices=[('efectivo', 'Efectivo'), ('transferencia', 'Transferencia'), ('débito', 'Débito'), ('crédito', 'Crédito')], max_length=15)),
                ('tipoDeComprobante', models.CharField(choices=[('A', 'Factura A'), ('B', 'Factura B'), ('C', 'Factura C')], max_length=15)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('clienteMayorista', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clienteMayorista', to='ventas.clientemayorista')),
            ],
        ),
        migrations.CreateModel(
            name='FacturaAfip',
            fields=[
                ('numeroComprobante', models.AutoField(primary_key=True, serialize=False)),
                ('fechaEmision', models.DateField()),
                ('venta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='facturaVenta', to='ventas.venta')),
            ],
        ),
        migrations.CreateModel(
            name='DetalleVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('subTotal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalleProducto', to='productos.producto')),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalleVenta', to='ventas.venta')),
            ],
        ),
    ]
