from django.shortcuts import get_object_or_404, redirect, render
from store.models import Producto, Variation
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, id_producto):
    producto = Producto.objects.get(id=id_producto)

    current_user = request.user

    if current_user.is_authenticated:
        #Aqui en este bloque agregaremos la logica del carrito de compras cuando el usuario esta autenticado
        producto_variation =[]

        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(producto=producto, variation_value__iexact=value)
                    producto_variation.append(variation)
                except:
                    pass
        
        is_cart_item_exists = CartItem.objects.filter(producto=producto, usuario=current_user).exists()

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(
                producto = producto,
                usuario = current_user
            )

            ex_var_list = []
            id = []

            for item in cart_item:
                exisiting_variation = item.variations.all()
                ex_var_list.append(list(exisiting_variation))
                id.append(item.id)
            
            if producto_variation in ex_var_list:
                index = ex_var_list.index(producto_variation)
                item_id = id[index]
                item = CartItem.objects.get(producto=producto, id=item_id)
                item.cantidad += 1
                item.save()
            else:
                item = CartItem.objects.create(producto= producto, cantidad=1, usuario=current_user)
                if len(producto_variation) > 0 :
                    item.variations.clear()
                    item.variations.add(*producto_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                producto = producto, 
                cantidad = 1,
                usuario = current_user
            )
            if len(producto_variation) > 0 :
                cart_item.variations.clear()
                cart_item.variations.add(*producto_variation)

            
            cart_item.save()
        return redirect('cart')

    else:
        producto_variation =[]

        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(producto=producto, variation_value__iexact=value)
                    producto_variation.append(variation)
                except:
                    pass
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(producto=producto, cart=cart).exists()

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(
                producto = producto,
                cart = cart
            )

            ex_var_list = []
            id = []

            for item in cart_item:
                exisiting_variation = item.variations.all()
                ex_var_list.append(list(exisiting_variation))
                id.append(item.id)
            
            if producto_variation in ex_var_list:
                index = ex_var_list.index(producto_variation)
                item_id = id[index]
                item = CartItem.objects.get(producto=producto, id=item_id)
                item.cantidad += 1
                item.save()
            else:
                item = CartItem.objects.create(producto= producto, cantidad=1, cart=cart)
                if len(producto_variation) > 0 :
                    item.variations.clear()
                    item.variations.add(*producto_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                producto = producto, 
                cantidad = 1,
                cart = cart
            )
            if len(producto_variation) > 0 :
                cart_item.variations.clear()
                cart_item.variations.add(*producto_variation)

            
            cart_item.save()
        return redirect('cart')

def remove_cart(request, id_producto, cart_item_id):
    
    producto = get_object_or_404(Producto, id=id_producto)
    
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(producto=producto, usuario=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))
            cart_item = CartItem.objects.get(producto = producto, cart = cart, id= cart_item_id)
       
        if cart_item.cantidad > 1:
            cart_item.cantidad -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    
    return redirect('cart')

def remove_cart_item(request, id_producto, cart_item_id):
    producto = get_object_or_404(Producto, id=id_producto)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(producto=producto, usuario=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(producto=producto, cart=cart, id=cart_item_id)

    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, cantidad=0, cart_items=None):
    envio = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(usuario=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.producto.precio * cart_item.cantidad)
            cantidad += cart_item.cantidad
        envio = 5000
        grand_total = total + envio
    except ObjectDoesNotExist:
        pass ##Solo ignora la excepcion

    context = {
        'total': total,
        'cantidad': cantidad,
        'cart_items': cart_items,
        'envio': envio,
        'grand_total': grand_total,
    }
    
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request,  total=0, cantidad=0, cart_items=None):
    envio = 0
    grand_total = 0
    try:

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(usuario=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
           total += (cart_item.producto.precio * cart_item.cantidad)
           cantidad += cart_item.cantidad
        envio = 5000
        grand_total = total + envio
    except ObjectDoesNotExist:
        pass ##Solo ignora la excepcion

    context = {
        'total': total,
        'cantidad': cantidad,
        'cart_items': cart_items,
        'envio': envio,
        'grand_total': grand_total,
    }

    return render(request, 'store/checkout.html', context)