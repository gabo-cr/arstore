# Generated by Django 4.1.7 on 2023-03-06 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0004_alter_detalle_product_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalle',
            name='imagenURI',
            field=models.TextField(null=True),
        ),
    ]
