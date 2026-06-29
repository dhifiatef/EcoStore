from django.db import models
from django.contrib.auth.models import User


class Store(models.Model):
    name = models.CharField(max_length=200)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Category(models.TextChoices):
    ELECTRONICS = 'electronics', 'Electronics'
    CLOTHING = 'clothing', 'Clothing'
    FOOD = 'food', 'Food & Beverages'
    BOOKS = 'books', 'Books'
    HOME = 'home', 'Home & Garden'
    SPORTS = 'sports', 'Sports & Outdoors'
    HEALTH = 'health', 'Health & Beauty'
    AUTOMOTIVE = 'automotive', 'Automotive'
    TOYS = 'toys', 'Toys & Games'
    OTHER = 'other', 'Other'


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.OTHER)
    sku = models.CharField(max_length=100, unique=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    image_url = models.URLField(blank=True, default='')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.store.name})"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    customer_name = models.CharField(max_length=200, default='Customer')
    customer_email = models.EmailField(default='customer@example.com')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} – {self.store.name}"


class Message(models.Model):
    sender_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='sent_messages')
    receiver_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender_store} to {self.receiver_store} @ {self.timestamp:%Y-%m-%d %H:%M}"
