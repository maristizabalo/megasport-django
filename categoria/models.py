from django.urls import reverse
from django.db import models

# Create your models here.
class Categoria(models.Model):
    categoria_nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=255, blank = True)
    slug = models.CharField(max_length=100, unique=True)
    imagen_categoria = models.ImageField(upload_to='photos/categorias', blank = True)


    def get_url(self):
        return reverse('productos_por_categoria', args=[self.slug])

        
    def __str__(self):
        return self.categoria_nombre
