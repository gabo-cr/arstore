# Generated by Django 4.1.7 on 2023-03-07 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0006_alter_cliente_correo_alter_cliente_direccion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='encabezado',
            name='total',
            field=models.FloatField(),
        ),
    ]
