# Generated by Django 4.1.7 on 2023-03-07 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0007_alter_encabezado_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detalle',
            name='precio',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='detalle',
            name='total',
            field=models.FloatField(),
        ),
    ]