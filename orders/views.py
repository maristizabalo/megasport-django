from django.http import JsonResponse
from django.shortcuts import render, redirect
from carts.models import CartItem
from store.models import Producto
from .forms import OrderForm
from .models import Order, OrderProduct
import datetime
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.


def payments(request):

# El order_numbre tiene un numero que es el id de cada order para ser mas especficos en el get 
# perono supe como traer ese order_umber desde place_order hasta esta pagina 
# ya que como esta en el momento va a generar error si se hacen dos pedidos el mismodia
#por el mismo usuario

    yr = int(datetime.date.today().strftime('%Y'))
    mt = int(datetime.date.today().strftime('%m')) 
    dt = int(datetime.date.today().strftime('%d'))

    d= datetime.date(yr, mt, dt)
    current_date = d.strftime("%Y%m%d")
    order_number = current_date
    order = Order.objects.get(usuario=request.user, is_ordered=False, order_number=order_number)

##Mover todos los carritos items hacia la tabla de orer product
    cart_items = CartItem.objects.filter(usuario=request.user)
    for item in cart_items:
        orderproduct=OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.usuario_id = request.user.id
        orderproduct.producto_id= item.producto_id
        orderproduct.cantidad = item.cantidad
        orderproduct.precio_producto = item.producto.precio
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()
    
        producto = Producto.objects.get(id=item.producto_id)
        producto.stock -= item.cantidad
        producto.save()

    CartItem.objects.filter(usuario=request.user).delete()

    mail_subject = 'Gracias por tu compra'
    body = render_to_string('orders/order_received_email.html', {
        'usuario': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, body, to=[to_email])
    send_email.send()

    return redirect('order_complete')


def place_order(request, total=0, cantidad=0):
    order_number = ''
    current_user = request.user
    cart_items = CartItem.objects.filter(usuario=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')
    
    grand_total=0
    envio=0

    for cart_item in cart_items:
        total += (cart_item.producto.precio*cart_item.cantidad)
        cantidad += cart_item.cantidad
    
    envio = 5000
    grand_total = total + envio

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            data = Order()
            data.usuario = current_user
            data.nombre = form.cleaned_data['nombre'] 
            data.apellido = form.cleaned_data['apellido']
            data.email = form.cleaned_data['email']
            data.numero = form.cleaned_data['numero']
            data.addres_line_1 = form.cleaned_data['addres_line_1']
            data.addres_line_2 = form.cleaned_data['addres_line_2']
            data.ciudad = form.cleaned_data['ciudad']
            data.barrio = form.cleaned_data['barrio']
            data.order_note = form.cleaned_data['order_note'] 
            data.order_total = grand_total
            data.envio = envio
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m')) 
            dt = int(datetime.date.today().strftime('%d'))

            d= datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date
            data.order_number = order_number
            data.save()

            order = Order.objects.get(usuario=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'order_number': order_number,
                'cart_items':cart_items,
                'total': total,
                'envio': envio,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')

def order_complete(request):
    usuario = request.user
    yr = int(datetime.date.today().strftime('%Y'))
    mt = int(datetime.date.today().strftime('%m')) 
    dt = int(datetime.date.today().strftime('%d'))

    d= datetime.date(yr, mt, dt)
    current_date = d.strftime("%Y%m%d")
    order_number = current_date
    order = Order.objects.get(usuario=usuario, is_ordered=False, order_number=order_number)
    context = {
        'order': order
    }
    return render(request, 'orders/order_complete.html', context)
