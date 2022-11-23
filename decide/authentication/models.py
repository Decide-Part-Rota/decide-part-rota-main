from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Persona(models.Model):
    usuario = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True,)
    sexo = models.CharField(max_length=30, blank=False)
    edad = models.PositiveSmallIntegerField()
    class Meta:
        managed = False
        db_table = 'persona'

@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Persona.objects.create(user=instance)
    instance.persona.save()
