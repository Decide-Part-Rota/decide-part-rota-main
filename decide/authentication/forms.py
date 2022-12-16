# -*- encoding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError 
from .models import Person
from django.contrib.auth.forms import UserCreationForm
from django_countries.fields import CountryField

sexos=[("woman","Woman"),("man","Man"),("other","Other")] 
status=[("single","Single"),("partner","Partner"),("married","Married"),("divorced","Divorced"),("widow","Widow")]
     


class PersonForm(UserCreationForm):
    sex = forms.ChoiceField(choices=sexos, required=True, label="Select your gender")
    age = forms.IntegerField(required=False)
    status = forms.ChoiceField(choices=status, required=True, label="Select your civil status")
    country = CountryField().formfield()
    class Meta:
          model=User
          fields=["username","password1","password2","email","sex","age","status","country"]

class CompleteForm(forms.Form):
    sex = forms.ChoiceField(choices=sexos, required=True)
    age = forms.IntegerField(required=True)
    status = forms.ChoiceField(choices=status, required=True, label="Select your civil status")
    country = CountryField().formfield()





# No se usa
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