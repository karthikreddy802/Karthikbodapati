from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from django.db import models
from django.conf import settings


class Restaurant(models.Model):

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending Approval"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    )

    name = models.CharField(max_length=200)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_restaurants",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    map_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
    )

    # ⭐ ADD THESE SETTINGS FIELDS

    description = models.TextField(
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    opening_time = models.TimeField(
        null=True,
        blank=True
    )

    closing_time = models.TimeField(
        null=True,
        blank=True
    )

    is_open = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name


# 🔹 Rating Model
class Rating(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.rating}"


# 🔹 Table Model
class Table(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="tables"
    )

    table_number = models.IntegerField()
    capacity = models.PositiveIntegerField(default=4, help_text="Number of guests")
    x_position = models.IntegerField(default=0)
    y_position = models.IntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )

    def __str__(self):
        return f"{self.restaurant.name} - Table {self.table_number}"


# 🔹 Menu Category
class MenuCategory(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"



# 🔹 Menu Item (Single Clean Food System)
from django.db import models
from .models import Restaurant, MenuCategory   # adjust import if needed

class MenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="menu_items",
        null=True,      # Temporary (to avoid migration error)
        blank=True
    )

    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.CASCADE,
        related_name="items"
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(max_length=500, blank=True)  # Optional image URL for menu item
    available = models.BooleanField(default=True)

    # Optional image URL for displaying the dish photo in menu UI
  
    def __str__(self):
        return f"{self.name} - ₹{self.price}"
from django.db import models

class WaitingList(models.Model):

    STATUS_CHOICES = (
        ('waiting', 'Waiting'),
        ('seated', 'Seated'),
        ('cancelled', 'Cancelled'),
    )

    restaurant = models.ForeignKey(
        'Restaurant',
        on_delete=models.CASCADE,
        related_name='waiting_list'
    )

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    guests = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='waiting'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        'MenuItem',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.item.name} ({self.quantity})"
