from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import GetUserView, LogoutView, RegisterView, loginForm, registerForm

from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('register/', RegisterView.as_view()),
    path('loginForm/', loginForm),
    path('registerForm/', registerForm),

    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', loginForm),
]
