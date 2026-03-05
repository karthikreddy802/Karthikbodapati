from django.db import models


class Reservation(models.Model):
    """Table booking for a date and time slot."""
    customer = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    table = models.ForeignKey(
        'restaurants.Table',
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    date = models.DateField()
    slot = models.CharField(max_length=20)  # e.g. "10-12", "12-14"
    guest_count = models.PositiveIntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'slot']
        unique_together = [['table', 'date', 'slot']]

    def __str__(self):
        return f"{self.customer.username} - {self.restaurant.name} - {self.date} {self.slot}"


class Waitlist(models.Model):
    customer = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE
    )

    restaurant = models.ForeignKey(
        'restaurants.Restaurant',   # 👈 THIS IS CORRECT
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.username} - {self.restaurant.name}"
