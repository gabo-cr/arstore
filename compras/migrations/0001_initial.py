# Generated by Django 4.1.7 on 2023-03-03 17:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Encabezado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numeroOrden', models.CharField(max_length=100, unique=True)),
                ('total', models.TextField()),
                ('fechaRegistro', models.DateTimeField()),
                ('moneda', models.CharField(max_length=15)),
                ('fechaActualizacion', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Detalle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=50)),
                ('nombre', models.TextField()),
                ('cantidad', models.IntegerField(default=0)),
                ('precio', models.TextField()),
                ('total', models.TextField()),
                ('product_id', models.CharField(max_length=50)),
                ('encabezado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compras.encabezado')),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField()),
                ('telefono', models.TextField()),
                ('correo', models.TextField()),
                ('direccion', models.TextField()),
                ('encabezado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compras.encabezado')),
            ],
        ),
    ]