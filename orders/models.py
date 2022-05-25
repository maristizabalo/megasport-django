from django.db import models
from cuentas.models import Cuenta
from store.models import Producto, Variation

# Create your models here.
class Payment(models.Model):
    usuario = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_id = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.payment_id


class Order(models.Model):

    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Aceptado'),
        ('Completed', 'Completado'),
        ('Canceled', 'Cancelado'),
    )

    usuario = models.ForeignKey(Cuenta, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    numero = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    addres_line_1 = models.CharField(max_length=100)
    addres_line_2 = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=50)
    barrio = models.CharField(max_length=50)
    order_note = models.CharField(max_length=250, blank=True)
    order_total = models.FloatField()
    envio = models.FloatField()
    status = models.CharField(max_length=50, choices=STATUS, default='New')
    ip = models.CharField(max_length=30, blank=True)
    is_ordered = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f'{self.nombre} {self.apellido}'

    def full_address(self):
        return f'{self.addres_line_1} {self.addres_line_2}'
        
    def __str__(self):
        return self.nombre
    
class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation, blank=True)
    cantidad = models.IntegerField()
    precio_producto = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.producto.nombre_producto






