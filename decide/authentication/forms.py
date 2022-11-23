# -*- encoding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError 
from .models import Persona
from django.contrib.auth.forms import UserCreationForm

sexos=[("mujer","Mujer"),("hombre","Hombre"),("otro","Otro")]

class RegisterForm(UserCreationForm):
    sexo = forms.ChoiceField(choices=sexos, required=True, label="Seleccione su sexo")
    edad = forms.IntegerField(required=True)
    
    class Meta:
     model=User
     fields=["username","password1","password2","email","sexo","edad"]



class LoginForm(forms.Form):
     username = forms.CharField(label='Usuario',widget=forms.TextInput,required=True)
     password = forms.CharField(label='Contraseña',widget=forms.PasswordInput,required=True)




'''
def clean(self):
       email = self.cleaned_data.get('email')
       if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")
       return self.cleaned_data
'''