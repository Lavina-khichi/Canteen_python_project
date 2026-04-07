from django.db import models
from django.contrib.auth.models import User

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=6, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.menu_item.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

class Table(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    number = models.IntegerField(unique=True)
    seats = models.IntegerField(default=12)
    available = models.BooleanField(default=True) 

    def __str__(self):
        return f"Table {self.number} with {self.seats} seats"

class Reservation(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    guest_name = models.CharField(max_length=100)
    guest_email = models.CharField(max_length=100)
    guest_phone = models.CharField(max_length=10)
    guest_count = models.IntegerField()
    guest_time = models.CharField(max_length=40)
    guest_message = models.TextField()
    reservation_time = models.DateField()

    def __str__(self):
        return f"Reservation for {self.guest_name} at Table {self.table.number} for {self.guest_count} guests"
    
class Cards(models.Model):
    account_holder_name = models.CharField(max_length=100)
    card_no = models.CharField(max_length=32)
    cvv = models.CharField(max_length=3)
    mm = models.CharField(max_length=2)
    yy = models.CharField(max_length=2)
    pay_done = models.BooleanField(default=False)


