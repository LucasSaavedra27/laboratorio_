# Generated by Django 4.2 on 2024-11-02 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_alter_empleado_fechadeingreso_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='empleado',
            name='estado',
            field=models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')], default='activo', max_length=10),
        ),
    ]
