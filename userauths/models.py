from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.utils import timezone
from shortuuid.django_fields import ShortUUIDField
import shortuuid
from django.db.models.signals import post_save



class User(AbstractUser):
    uid = ShortUUIDField(length=10, max_length=10, alphabet=shortuuid.get_alphabet())
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
