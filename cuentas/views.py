from django.shortcuts import get_object_or_404, render, redirect
from cuentas.forms import RegistrationForm, UserForm, UserProfileForm
from .models import Cuenta, UserProfile
from orders.models import Order
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from carts.views import _cart_id
from carts.models import Cart, CartItem

# Create your views here.

def registrar(request):
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            numero = form.cleaned_data['numero']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            usuario = email.split('@')[0]
            user = Cuenta.objects.create_user(nombre=nombre, apellido=apellido, email=email, password=password, usuario=usuario)
            user.numero = numero
            user.save()

            profile = UserProfile()
            profile.usuario_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()

            """current_site = get_current_site(request)
            mail_subject = 'Por favor activa tu cuenta en MegaSport'
            body = render_to_string('cuentas/cuenta_verification_email.html', {
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,body,to=[to_email])
            send_email.send()"""


            #messages.success(request, 'Se registro exitosamente')
            return redirect('/cuentas/login/?command=verification&email='+email)


    context = {
        'form': form
    }
    return render(request, 'cuentas/registrar.html', context)

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:

            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists= CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    producto_variation = []

                    for item in cart_item:
                        variation = item.variations.all()
                        producto_variation.append(list(variation))
                    
                    cart_item = CartItem.objects.filter(usuario=user)
                    ex_var_list = []
                    id = []

                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                        
                    for pr in producto_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.cantidad += 1
                            item.usuario = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.usuario = user
                                item.save()
            except:
                pass

            #http://localhost:8000/cuentas/login/?next=/cart/checkout

            auth.login(request, user)
            messages.success(request, 'Has iniciado sesion exitosamente')

            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                #solo capturar el parametro next
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
                    
            except:
                return redirect('home') 

        else:
            messages.error(request, 'Las credenciales son incorrectas')
            return redirect('login')



    return render(request, 'cuentas/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Has cerrado sesion')

    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Cuenta._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Cuenta.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request, 'Felicidades, tu cuenta esta activa!')
        return redirect('login')
    else:
        messages.error(request, ' La activacion es invalida')
        return redirect('registrar')


@login_required(login_url = 'login')
def dashboard(request):
    orders = Order.objects.order_by('-create_at').filter(usuario_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    userprofile = UserProfile.objects.get(usuario_id=request.user.id)
    context = {
        'orders_count':orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'cuentas/dashboard.html',context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Cuenta.objects.filter(email=email).exists():
            user = Cuenta.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Recuperar contraseña'
            body = render_to_string('cuentas/reset_password_email.html', {
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,body, to=[to_email])
            send_email.send()

            messages.success(request, 'Un email fue enviado a tu bandeja de entrada para resetear tu password')
            return redirect('login')
        else:
            messages.error(request, 'La cuenta de usuario no existe')
            return redirect('forgotPassword')
    return render(request, 'cuentas/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Cuenta._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Cuenta.DoesNotExist):
        user=None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Por favor resetea tu contraseña')
        return redirect('resetPassword')
    else:
        messages.error(request, 'El link ha expirado')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Cuenta.objects.get(pk=uid)
            user.set_password(password)
            user.save()

            messages.success(request, 'El password se reseteo correctamente')
            return redirect('login')
        else:
            messages.error(request, 'El password no concuerda')
            return redirect('resetPassword')
    else:
        return render(request, 'cuentas/resetPassword.html')

def my_orders(request):
    orders = Order.objects.filter(usuario=request.user, is_ordered=True).order_by('-create_at')
    context={
        'orders' : orders,
    }
    return render(request, 'cuentas/my_orders.html', context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, usuario=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Su informacion fue guardada con exito')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    
    context={
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }

    return render(request, 'cuentas/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Cuenta.objects.get(usuario__exact=request.user.usuario)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()

                messages.success(request, 'El password se actualizo correctamente')
                return redirect('change_password')
            else:
                messages.error(request, 'Por favor ingrese un password valido')
                return redirect('change_password')
        else:
            messages.error(request, 'El password no coincide')
            return redirect('change_password')
    return render(request, 'cuentas/change_password.html')