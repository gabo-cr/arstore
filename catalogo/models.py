from django.db import models
from django.utils import timezone

class Articulo(models.Model):
    sku = models.CharField(blank=False, null=False, max_length=50)
    imagenURI = models.TextField(null=True)
    nombre = models.TextField(blank=False, null=False)
    cantidad = models.IntegerField(blank=False, null=False, default=0)
    fechaRegistro = models.DateTimeField(null=False)
    ultimaFechaActualizacion = models.DateTimeField(null=False)
    sincronizado = models.DateTimeField(default=timezone.now)
    product_id = models.CharField(blank=False, null=False, unique=True, max_length=50)

    def __str__(self):
        return self.nombre


class LogArticulo(models.Model):
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    json = models.TextField(blank=False, null=False)
    fechaRegistro = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.articulo.nombre