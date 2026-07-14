from django.contrib import admin
# ទាញយក class models ទាំងអស់ចេញពី models.py ក្នុង App ជាមួយគ្នា
from .models import Category, Shop, Product, Order, OrderItem

# ==========================================================
# 1. ចុះឈ្មោះម៉ូដែលចាស់ៗរបស់អ្នកដែលមានស្រាប់
# ==========================================================
admin.site.register(Category)
admin.site.register(Shop)
admin.site.register(Product)

# ==========================================================
# 2. បង្កើត Inline សម្រាប់បង្ហាញមុខទំនិញកូនៗនៅក្នុងទំព័រ Order មេ
# ==========================================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # មិនបាច់បង្ហាញប្រអប់ទទេសម្រាប់ថែមទំនិញឡើយ
    readonly_fields = ['product', 'quantity', 'price']  # ទុកឱ្យ Admin មើលតែមិនឱ្យកែប្រែទិន្នន័យទិញរបស់ភ្ញៀវទេ

# ==========================================================
# 3. ចុះឈ្មោះម៉ូដែល Order រួមទាំងការកំណត់ការបង្ហាញទិន្នន័យ (Admin Customization)
# ==========================================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # បង្ហាញជា Columns លើតារាង Admin ឱ្យងាយស្រួលមើល
    list_display = ['id', 'user', 'total_price', 'status', 'created_at']
    
    # បង្ហាញប្រអប់ខាងស្តាំសម្រាប់ចុច Filter មើលតាមស្ថានភាព និងកាលបរិច្ឆេទ
    list_filter = ['status', 'created_at']
    
    # បញ្ចូលមុខទំនិញដែលភ្ញៀវបានកុម្ម៉ង់ ឱ្យមកបង្ហាញរួមគ្នាក្នុងទំព័រលម្អិតនៃ Order តែម្តង
    inlines = [OrderItemInline]