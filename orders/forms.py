from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['nombre', 'apellido', 'numero', 'email', 'addres_line_1', 'addres_line_2', 'ciudad', 'barrio', 'order_note']
