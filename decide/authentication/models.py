from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Person(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    sex = models.CharField(max_length=30, blank=False)
    age = models.PositiveIntegerField()
    
    def __str__(self):
        return self.user.username
'''
@receiver(post_save, sender=User)
def update_person_signal(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(user=instance)
    instance.person.save()
'''


