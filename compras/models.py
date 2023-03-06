from django.db import models
from django.utils import timezone

class Encabezado(models.Model):
    numeroOrden = models.CharField(blank=False, null=False, max_length=50)
    total = models.TextField(null=False)
    fechaRegistro = models.DateTimeField(null=False)
    moneda = models.CharField(blank=False, null=False, max_length=15)
    fechaActualizacion = models.DateTimeField(null=True)
    orden_id = models.CharField(blank=False, null=False, unique=True, max_length=50)

    def __str__(self):
        return self.numeroOrden
    
class Detalle(models.Model):
    encabezado = models.ForeignKey(Encabezado, on_delete=models.CASCADE)
    sku = models.CharField(blank=False, null=False, max_length=50)
    nombre = models.TextField(blank=False, null=False)
    cantidad = models.IntegerField(blank=False, null=False, default=0)
    precio = models.TextField(null=False)
    total = models.TextField(null=False)
    product_id = models.CharField(null=True, max_length=50)
    imagenURI = models.TextField(null=True)

    def __str__(self):
        return self.encabezado.numeroOrden

class Cliente(models.Model):
    encabezado = models.ForeignKey(Encabezado, on_delete=models.CASCADE)
    nombre = models.TextField(blank=False, null=False, default='')
    telefono = models.TextField(blank=False, null=False, default='')
    correo = models.TextField(blank=False, null=False, default='')
    direccion = models.TextField(blank=False, null=False, default='')

    def __str__(self):
        return self.encabezado.numeroOrden