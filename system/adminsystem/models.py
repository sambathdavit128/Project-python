from django.db import models
from django.contrib.auth.models import User

# ==========================================================
# 1. ម៉ូដែលប្រភេទហាង (Category Model)
# ==========================================================
class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

# ==========================================================
# 2. ម៉ូដែលហាង (Shop Model)
# ==========================================================
class Shop(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='shop_images/', blank=True, null=True)
    
    def __str__(self):
        return self.name

# ==========================================================
# 3. ម៉ូដែលផលិតផល (Product Model)
# ==========================================================
class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name

# ==========================================================
# 4. ម៉ូដែលការបញ្ជាទិញ (Order Model - មេ)
# ==========================================================
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    # ភ្ជាប់ទៅកាន់ User ដែលបាន Login (null=True អនុញ្ញាតឱ្យទិញដោយមិនបាច់ Login ក៏បាន បើអ្នកចង់)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

# ==========================================================
# 5. ម៉ូដែលមុខទំនិញក្នុង Order (OrderItem Model - កូន)
# ==========================================================
class OrderItem(models.Model):
    # ភ្ជាប់ទៅកាន់ Order មេខាងលើ
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # ភ្ជាប់ទៅកាន់ Product ដែលមានស្រាប់របស់អ្នក
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) # រក្សាទុកតម្លៃផលិតផលនាពេលបញ្ជាទិញ

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"