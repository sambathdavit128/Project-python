from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal  # នាំចូល Decimal សម្រាប់គណនាតម្លៃលុយឱ្យបានត្រឹមត្រូវ

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
    
    # --- បន្ថែម Fields ថ្មីៗសម្រាប់ព័ត៌មានហាងនៅទីនេះ ---
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="លេខទូរស័ព្ទហាង"
    )
    address = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="ទីតាំង/អាសយដ្ឋានហាង"
    )
    opening_time = models.TimeField(
        blank=True, 
        null=True, 
        verbose_name="ម៉ោងបើកលក់"
    )
    closing_time = models.TimeField(
        blank=True, 
        null=True, 
        verbose_name="ម៉ោងបិទលក់"
    )
    
    def __str__(self):
        return self.name

# ==========================================================
# 3. ម៉ូដែលផលិតផល (Product Model)
# ==========================================================
class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)  # បន្ថែម field រូបភាពសម្រាប់ផលិតផល
    
    # --- បន្ថែម Fields ថ្មីសម្រាប់ព័ត៌មានបន្ថែម និងការបញ្ចុះតម្លៃ ---
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="ការពិពណ៌នាផលិតផល"
    )
    discount = models.IntegerField(
        default=0, 
        verbose_name="ការបញ្ចុះតម្លៃ (%)"
    )  # ឧទាហរណ៍៖ បញ្ចូលលេខ 5 សម្រាប់បញ្ចុះតម្លៃ 5%

    # --- បង្កើត Property សម្រាប់គណនាតម្លៃដែលដក Discount រួច (final_price) ---
    @property
    def final_price(self):
        if self.discount > 0:
            # រូបមន្ត៖ Price - (Price * Discount / 100)
            discount_amount = self.price * (Decimal(self.discount) / Decimal(100))
            return round(self.price - discount_amount, 2)
        return self.price

    # --- បង្កើត Property បន្ថែម (discounted_price) ដើម្បីកុំឱ្យមានបញ្ហាជាមួយកូដចាស់ ឬ HTML ផ្សេងទៀត ---
    @property
    def discounted_price(self):
        return self.final_price

    # --- បង្កើត Property (discount_percentage) សម្រាប់ម៉ាស៊ីន loop ផ្សេងទៀតដែលហៅរកឈ្មោះនេះ ---
    @property
    def discount_percentage(self):
        return self.discount
    
    def __str__(self):
        return self.name

# ==========================================================
# 4. ម៉ូដែលការបញ្ជាទិញ (Order Model - មេ)
# ==========================================================
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # បានកែប្រែពី max_digits=20 ទៅជា max_length=20 ត្រង់នេះរួចរាល់ហើយ
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ព័ត៌មានទំនាក់ទំនងរបស់ភ្ញៀវ
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

# ==========================================================
# 5. ម៉ូដែលមុខទំនិញក្នុង Order (OrderItem Model - កូន)
# ==========================================================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"