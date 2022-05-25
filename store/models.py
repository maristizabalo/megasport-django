from django.db import models
from django.urls import reverse
from categoria.models import Categoria
from cuentas.models import Cuenta
from django.db.models import Avg, Count
# Create your models here.
class Producto(models.Model):
    nombre_producto = models.CharField(max_length=200, unique=True)
    slug = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(max_length=500, blank=True)
    precio = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('detalle_producto', args=[self.categoria.slug, self.slug])
    
    def __str__(self):
        return self.nombre_producto
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(producto=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    def countReview(self):
        reviews = ReviewRating.objects.filter(producto=self, status=True).aggregate(count=Count('id'))
        count=0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

class Variation(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    variation_value=models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.variation_value

class ReviewRating(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.CharField(max_length=800, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject