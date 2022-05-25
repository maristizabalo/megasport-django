from distutils.command.upload import upload
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self, nombre, apellido, usuario, email, password=None):
        if not email:
            raise ValueError('El usuario debe tener un email')

        if not usuario:
            raise ValueError('El usuario debe tener un nombre de usuario')

        user = self.model(
            email = self.normalize_email(email),
            usuario = usuario,
            nombre = nombre,
            apellido = apellido
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nombre, apellido, usuario, email, password):
        user = self.create_user(
            email = self.normalize_email(email),
            usuario=usuario,
            nombre=nombre,
            apellido=apellido,
            password=password
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user   


class Cuenta(AbstractBaseUser):
    
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    usuario = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=50, unique=True)
    numero = models.CharField(max_length=50)

    #campos atributos de django
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)

    #CAMPO PARA INICIAR SESION DEBE SER EL EMAIL NO EL USERNAME COMO POR DEFECTO VIENE CONFIGURADO EN DJANGO

    USERNAME_FIELD = 'email'

    #CAMPOS REQUERIDOS A LA HORA DE REGISTRARSE COMO USUARIO
    REQUIRED_FIELDS = ['usuario', 'nombre', 'apellido']

    objects = MyAccountManager()

    def full_name(self):
        return f'{self.nombre} {self.apellido}'
    def __str__(self):
        return self.email

    #tiene permisos
    def has_perm(self, permiso, obj=None):
        return self.is_admin
    
    #tiene acceso a los modulos
    def has_module_perms(self, add_label):
        return True

class UserProfile(models.Model):
    usuario = models.OneToOneField(Cuenta, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=100, blank=True)
    address_line_2 = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(blank=True, upload_to="userprofile")
    ciudad = models.CharField(blank=True, max_length=20)
    barrio = models.CharField(blank=True, max_length=20)

    def __str__(self):
        return self.usuario.nombre
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'