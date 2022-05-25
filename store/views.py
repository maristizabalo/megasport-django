from django.shortcuts import redirect, render, get_object_or_404
from carts.models import CartItem
from categoria.models import Categoria
from .models import Producto, ReviewRating
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct

# Create your views here.
def store(request, categoria_slug=None):
    categorias = None
    productos = None
    contar_productos = 0
    if categoria_slug != None:
        categorias = get_object_or_404(Categoria, slug=categoria_slug) 
        productos = Producto.objects.filter(categoria= categorias, is_available=True).order_by('id')
        paginator = Paginator(productos, 6)
        page = request.GET.get('page')
        page_products = paginator.get_page(page)
        contar_productos = productos.count()
    else:
        productos = Producto.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(productos, 6)
        page = request.GET.get('page')
        page_products = paginator.get_page(page)
        contar_productos = productos.count()

    context = {
        'productos': page_products,
        'contar_productos': contar_productos,
    }   
   
    return render(request, 'store/store.html', context)

def detalle_producto(request, categoria_slug, producto_slug):
    try:
        single_product = Producto.objects.get(categoria__slug=categoria_slug, slug=producto_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), producto=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(usuario=request.user, producto_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
        
    
    reviews= ReviewRating.objects.filter(producto_id=single_product.id, status=True)

    
    context ={
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
    }
    return render(request, 'store/detalle_producto.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            productos = Producto.objects.order_by('-created_date').filter( Q(descripcion__icontains=keyword) | Q(nombre_producto__icontains=keyword))
            contar_productos = productos.count()
    context = {
        'productos': productos,
        'contar_productos': contar_productos,
    }

    return render(request, 'store/store.html', context)

def submit_review(request, producto_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(usuario__id=request.user.id, producto__id=producto_id)
            form = ReviewForm(request.POST, instance= reviews)
            form.save()
            messages.success(request, 'Muchas gracias!, tu comentario ha sido actualizado')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.producto_id = producto_id
                data.usuario_id = request.user.id
                data.save()
                messages.success(request, 'Muchas gracias, tu comentario fue enviado con exito!')
                return redirect(url)
        