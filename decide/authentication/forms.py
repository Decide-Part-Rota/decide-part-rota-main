# -*- encoding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError 
sexos=[("mujer","Mujer"),("hombre","Hombre"),("otro","Otro")]

class RegisterForm(forms.Form):
    username = forms.CharField(label='Usuario',widget=forms.TextInput,required=True)
    email = forms.CharField(label='Email',widget=forms.EmailInput,required=True)
    password = forms.CharField(label='Contraseña',widget=forms.PasswordInput,required=True)
    sexo = forms.ChoiceField(choices=sexos, required=True, label="Seleccione su sexo")
    edad = forms.IntegerField(required=True)
    
    
    
    def clean(self):
       email = self.cleaned_data.get('email')
       if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")
       return self.cleaned_data