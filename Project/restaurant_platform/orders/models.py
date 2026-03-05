from django.db import models
from django.conf import settings


# =========================
# CART MODELS
# =========================

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders_cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    menu_item = models.ForeignKey(
        "restaurants.MenuItem",
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.menu_item.price * self.quantity

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"


# =========================
# ORDER MODELS
# =========================

class Order(models.Model):

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    )

    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    menu_item = models.ForeignKey(
        "restaurants.MenuItem",
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.menu_item.price * self.quantity

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"
