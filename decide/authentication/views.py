from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout

from .serializers import UserSerializer
from .forms import PersonForm, LoginForm, CompleteForm
from .models import Person
from verify_email.email_handler import send_verification_email


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm


from django.contrib.auth.decorators import login_required

class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)

class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})

class RegisterView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)

def loginForm(request):
    if request.method=="POST":
        form = LoginForm(request.POST)
        if(form.is_valid()):
            infForm = form.cleaned_data
            userOrEmail = infForm['usernameOrEmail']
            passwd= infForm['password']
            for user in User.objects.all():
                                                                                #el check password comprueba la pass de la base de datos y que hemos metido
                if (user.username == userOrEmail or user.email == userOrEmail) and check_password(passwd, user.password):
                    usernameDb=userOrEmail
                    if '@' in userOrEmail:
                        usernameDb=User.objects.get(email=userOrEmail).username




                    return render(request,'welcome.html')
            msgErrorLogin="Usuario o contraseña incorrectos"
            return render(request, 'login.html', {'msgErrorLogin':msgErrorLogin, 'loginForm':form})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'loginForm':form})
   
def register(request):
    form= PersonForm()
    if request.method=="POST":
        form=PersonForm(request.POST)
        if form.is_valid():
            
            username = form.cleaned_data.get('username')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            email= form.cleaned_data.get('email')
            sex = form.cleaned_data.get('sex')
            age = form.cleaned_data.get('age')
            status = form.cleaned_data.get('status')
            country = form.cleaned_data.get('country')
            discord_account = form.cleaned_data.get('discord_account')

            inactive_user = send_verification_email(request, form)
            person1=Person(user=inactive_user,sex=sex,age=age,status=status,country=country,discord_account=discord_account)

            person1.save()

            return redirect('/')
    return render(request,'register.html',{'form':form})   

@login_required(login_url='authentication/accounts/login/')
def welcome(request):
    usuario = request.user
    print(request.user)
    return render(request, 'welcome.html', {'user':usuario})

def anonymous(request):
    return render(request, 'anonymous.html')

def salir(request):
    logout(request)
    return redirect('/')

def complete(request):
    if request.user.is_authenticated and not Person.objects.filter(user = request.user.id).exists():
        user = request.user
        form=CompleteForm
        
        if request.method=="POST":
            form=CompleteForm(request.POST)

            if form.is_valid():
                sex = form.cleaned_data.get('sex')
                age = form.cleaned_data.get('age')
                status = form.cleaned_data.get('status')
                country = form.cleaned_data.get('country')
                discord_account = form.cleaned_data.get('discord_account')

                person = Person(user = user, sex = sex, age = age, status = status, country = country, discord_account = discord_account)
                person.save()

                return redirect('/')

        return render(request,'complete.html',{'form':form})
    else:
        return redirect('/')

def profileView(request):
    user = request.user
    person = Person.objects.get(user = user.id)
    context = {'username': user.username, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name, 'sex': person.sex,
                    'discord_account': person.discord_account, 'age': person.age}
    return render(request, 'profile.html', context)        

def editProfile(request):
    user = request.user
    new_disc_account = request.POST['discord_account']
    new_age=request.POST['age']
    person = Person.objects.get(user = User.objects.get(id=request.user.id))
    person.age=new_age
    person.discord_account = new_disc_account
    person.save()
    return redirect('/authentication/profile/')

