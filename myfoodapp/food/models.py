from django.db import models
from django.core.exceptions import ValidationError


# Create your models here.

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class CafeItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to='cafe_items/')

    def clean(self):
        # limit total items to 20
        if CafeItem.objects.count() >= 20 and not self.pk:
            raise ValidationError("Only 20 cafe items are allowed.")

    from django.db import models

class Feedback(models.Model):
    RATING_CHOICES = [
        (1, "1 - Poor"),
        (2, "2 - Okay"),
        (3, "3 - Good"),
        (4, "4 - Very Good"),
        (5, "5 - Excellent"),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.rating}"


    def __str__(self):
        return self.name
