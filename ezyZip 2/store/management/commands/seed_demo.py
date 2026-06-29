import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Store, Product, Order, Message, Category


DEMO_PRODUCTS = [
    # Electronics
    ("Wireless Earbuds Pro", "electronics", 79.99, 45),
    ("USB-C Hub 7-in-1", "electronics", 39.99, 120),
    ("Mechanical Keyboard RGB", "electronics", 129.99, 30),
    ("Portable SSD 1TB", "electronics", 89.99, 60),
    ("Smart LED Desk Lamp", "electronics", 34.99, 80),
    # Clothing
    ("Merino Wool Hoodie", "clothing", 69.99, 200),
    ("Running Shorts Pro", "clothing", 29.99, 350),
    ("Waterproof Hiking Boots", "clothing", 119.99, 75),
    # Home
    ("Bamboo Cutting Board Set", "home", 24.99, 150),
    ("Air Purifier HEPA", "home", 149.99, 25),
    ("Minimalist Wall Clock", "home", 44.99, 60),
    # Sports
    ("Resistance Bands Set", "sports", 19.99, 400),
    ("Yoga Mat Premium", "sports", 49.99, 180),
    ("Adjustable Dumbbell 20kg", "sports", 89.99, 40),
    # Books
    ("Clean Code (Paperback)", "books", 35.99, 90),
    ("The Lean Startup", "books", 22.99, 110),
    # Food
    ("Organic Green Tea 100g", "food", 14.99, 500),
    ("Cold Brew Coffee Kit", "food", 29.99, 200),
    # Health
    ("Vitamin D3 + K2 Gummies", "health", 18.99, 300),
    ("Collagen Peptides Powder", "health", 39.99, 150),
]

IMAGE_URLS = {
    "electronics": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80",
    "clothing": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80",
    "home": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&q=80",
    "sports": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&q=80",
    "books": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&q=80",
    "food": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&q=80",
    "health": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&q=80",
    "other": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=400&q=80",
}

STORE_CONFIGS = [
    {
        "username": "alice",
        "store": "Alice's Tech Emporium",
        "desc": "Premium electronics and tech accessories for modern life.",
        "products": DEMO_PRODUCTS[:7],
    },
    {
        "username": "bob",
        "store": "Bob's Lifestyle Co.",
        "desc": "Quality lifestyle products — from fitness to home essentials.",
        "products": DEMO_PRODUCTS[7:14],
    },
    {
        "username": "carol",
        "store": "Carol's Wellness Hub",
        "desc": "Everything you need to live healthy and well.",
        "products": DEMO_PRODUCTS[14:],
    },
]

ORDER_STATUSES = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
CUSTOMER_NAMES = ['Jordan Lee', 'Sam Rivera', 'Taylor Kim', 'Morgan Chen', 'Casey Brooks']


class Command(BaseCommand):
    help = 'Seed the database with demo stores, products, orders, and messages.'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding demo data...')

        stores = []
        for cfg in STORE_CONFIGS:
            user, created = User.objects.get_or_create(username=cfg['username'])
            if created:
                user.set_password('demo1234')
                user.email = f"{cfg['username']}@example.com"
                user.save()
                self.stdout.write(f"  ✓ Created user: {cfg['username']}")

            store, _ = Store.objects.get_or_create(
                owner=user,
                defaults={'name': cfg['store'], 'description': cfg['desc']}
            )
            stores.append(store)

            # Products
            for i, (name, cat, price, stock) in enumerate(cfg['products']):
                sku = f"{cfg['username'].upper()}-{cat[:3].upper()}-{i+1:03d}"
                Product.objects.get_or_create(
                    sku=sku,
                    defaults={
                        'name': name,
                        'price': Decimal(str(price)),
                        'stock': stock,
                        'category': cat,
                        'store': store,
                        'image_url': IMAGE_URLS.get(cat, IMAGE_URLS['other']),
                        'description': f"High-quality {name.lower()} from {store.name}.",
                    }
                )

            # Orders
            for j in range(8):
                total = Decimal(str(round(random.uniform(20, 500), 2)))
                from django.utils import timezone
                from datetime import timedelta
                days_ago = random.randint(0, 180)
                Order.objects.create(
                    store=store,
                    total=total,
                    status=random.choice(ORDER_STATUSES),
                    customer_name=random.choice(CUSTOMER_NAMES),
                    customer_email=f"customer{j}@example.com",
                    created_at=timezone.now() - timedelta(days=days_ago),
                )

        # Cross-store messages
        if len(stores) >= 2:
            pairs = [(stores[0], stores[1]), (stores[1], stores[2]), (stores[0], stores[2])]
            for s1, s2 in pairs:
                if not Message.objects.filter(sender_store=s1, receiver_store=s2).exists():
                    Message.objects.create(
                        sender_store=s1, receiver_store=s2,
                        content=f"Hi {s2.name}! Love your products. Any bulk discounts available?"
                    )
                    Message.objects.create(
                        sender_store=s2, receiver_store=s1,
                        content=f"Hey {s1.name}! Yes, we offer 10% off for orders over $200. Let's connect!"
                    )

        # Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')
            self.stdout.write('  ✓ Created superuser: admin / admin1234')

        self.stdout.write(self.style.SUCCESS('\n✅ Demo data seeded successfully!'))
        self.stdout.write('  Login credentials:')
        for cfg in STORE_CONFIGS:
            self.stdout.write(f"  • {cfg['username']} / demo1234  →  {cfg['store']}")
        self.stdout.write('  • admin / admin1234  →  Django Admin')
