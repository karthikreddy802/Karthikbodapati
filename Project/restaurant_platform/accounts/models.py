
from django.contrib.auth.models import AbstractUser
from django.db import models
from restaurants.models import Restaurant

class User(AbstractUser):

    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('restaurant_admin', 'Restaurant Admin'),
        ('customer', 'Customer'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES,default="customer")

    restaurant = models.ForeignKey(
        Restaurant,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
class Restaurant(models.Model):
    name = models.CharField(max_length=200)

    location = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    map_url = models.URLField(
        max_length=500,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name
