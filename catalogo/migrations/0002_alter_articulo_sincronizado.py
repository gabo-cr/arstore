# Generated by Django 4.1.7 on 2023-03-02 17:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articulo',
            name='sincronizado',
            field=models.DateTimeField(default=datetime.datetime(2023, 3, 2, 17, 25, 24, 296406, tzinfo=datetime.timezone.utc)),
        ),
    ]