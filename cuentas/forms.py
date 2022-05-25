from django import forms
from .models import Cuenta, UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Ingrese Password',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirme Password',
        'class': 'form-control',
    }))
    class Meta:
        model = Cuenta
        fields = ['nombre', 'apellido', 'numero', 'email', 'password']
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['placeholder'] = 'Ingrese Nombre'
        self.fields['apellido'].widget.attrs['placeholder'] = 'Ingrese Apellido'
        self.fields['numero'].widget.attrs['placeholder'] = 'Ingrese Telefono'
        self.fields['email'].widget.attrs['placeholder'] = 'Ingrese Email'

        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

    
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "El password no coincide!"
            )
    
class UserForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ('nombre','apellido','numero')
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid': ('Solo archivos de imagen')}, widget=forms.FileInput)
    class Meta:
        model= UserProfile
        fields = ('address_line_1', 'address_line_2', 'ciudad', 'barrio', 'profile_picture')
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
    
    