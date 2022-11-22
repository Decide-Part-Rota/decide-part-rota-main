from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Persona(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    sexo = models.CharField(max_length=30, blank=False)
    edad = models.PositiveSmallIntegerField()