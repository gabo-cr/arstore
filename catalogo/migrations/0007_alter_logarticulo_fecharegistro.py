# Generated by Django 4.1.7 on 2023-03-03 01:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0006_alter_articulo_sincronizado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logarticulo',
            name='fechaRegistro',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]