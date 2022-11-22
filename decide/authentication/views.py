from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.contrib.auth.hashers import check_password
from .serializers import UserSerializer
from .forms import RegisterForm, LoginForm
from django.http import HttpResponseRedirect
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


# def loginForm(request):
#     if request.method=="POST":
#         form = LoginForm(request.POST)
#         if(form.is_valid()):
#             infForm = form.cleaned_data
#             userOrEmail = infForm['usernameOrEmail']
#             passwd= infForm['password']
#             for user in User.objects.all():
#                                                                                 #el check password comprueba la pass de la base de datos y que hemos metido
#                 if (user.username == userOrEmail or user.email == userOrEmail) and check_password(passwd, user.password):
#                     usernameDb=userOrEmail
#                     if '@' in userOrEmail:
#                         usernameDb=User.objects.get(email=userOrEmail).username
#                     request.user=user
#                     return render(request,'welcome.html')
#             msgErrorLogin="Usuario o contraseña incorrectos"
#             return render(request, 'login.html', {'msgErrorLogin':msgErrorLogin, 'loginForm':form})
#     else:
#         form = LoginForm()
#     return render(request, 'login.html', {'loginForm':form})

def registerForm(request):
    form = RegisterForm()

    return render(request, 'register.html', {'registerForm':form})

@login_required(login_url='authentication/accounts/login/')
def welcome(request):
    print(request.user)
    return render(request, 'welcome.html')

