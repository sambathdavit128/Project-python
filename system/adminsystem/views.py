from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# ទាញយក class models ទាំងអស់ចេញពី models.py មកប្រើជាមួយគ្នា
from .models import Category, Shop, Product, Order, OrderItem 

# ==========================================================
# 1. Logic បង្ហាញទំព័រដើមទិញទំនិញ (Index / Shops & Products)
# ==========================================================
def index(request):
    # ទាញយកទិន្នន័យ "ហាងទាំងអស់ (Shops)" និង "ផលិតផលទាំងអស់ (Products)" ចេញពី Database ទៅបង្ហាញលើទំព័រដើម
    shops = Shop.objects.all()
    products = Product.objects.all()
    return render(request, 'index.html', {
        'shops': shops,
        'products': products
    })

# ==========================================================
# 2. View សម្រាប់បង្ហាញព័ត៌មានលម្អិត និងផលិតផលក្នុងហាងនីមួយៗ (Shop Detail)
# ==========================================================
def shop_detail(request, shop_id):
    # 1. ទាញយកទិន្នន័យហាងណាដែលមាន id ស្មើនឹង shop_id បើរកមិនឃើញឱ្យចេញទំព័រ Error 404
    shop = get_object_or_404(Shop, id=shop_id)
    
    # 2. ទាញយកផលិតផលទាំងអស់ដែលបានភ្ជាប់ជាមួយហាង (Shop) មួយនេះមកបង្ហាញ
    products = Product.objects.filter(shop=shop)
    
    # 3. បោះទាំងទិន្នន័យ shop និង products ទៅកាន់ទំព័រ template HTML
    return render(request, 'shop_detail.html', {
        'shop': shop,
        'products': products
    })

# ==========================================================
# 3. Logic សម្រាប់ចុះឈ្មោះអ្នកប្រើប្រាស់ (Register)
# ==========================================================
def register_view(request):
    if request.method == "POST":
        u_name = request.POST.get('username')
        e_mail = request.POST.get('email')
        p_word = request.POST.get('password')
        
        if User.objects.filter(username=u_name).exists():
            messages.error(request, "ឈ្មោះអ្នកប្រើប្រាស់នេះមានគេប្រើរួចហើយ!")
            return render(request, 'register.html')
            
        user = User.objects.create_user(username=u_name, email=e_mail, password=p_word)
        user.save()
        
        messages.success(request, "ចុះឈ្មោះជោគជ័យ! សូមធ្វើការ Login។")
        return redirect('login') 
        
    return render(request, 'register.html')

# ==========================================================
# 4. Logic សម្រាប់ចូលប្រើប្រាស់ប្រព័ន្ធ (Login)
# ==========================================================
def login_view(request):
    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('user_list')
            return redirect('index') 
        else:
            messages.error(request, "ឈ្មោះអ្នកប្រើប្រាស់ ឬលេខសម្ងាត់មិនត្រឹមត្រូវទេ!")
            
    return render(request, 'login.html')

# ==========================================================
# 5. Logic សម្រាប់ចាកចេញពីប្រព័ន្ធ (Logout)
# ==========================================================
def logout_view(request):
    logout(request) 
    return redirect('login') 

# ==========================================================
# 6. Logic មើលបញ្ជីឈ្មោះ User (ត្រូវ Login ជា Superadmin ជាមុនសិន)
# ==========================================================
def user_list_view(request):
    error = None
    accessed = False  # កំណត់តម្លៃលំនាំដើមជាមុនសិន ដើម្បីជៀសវាង error UnboundLocalError
    
    # លក្ខខណ្ឌតឹងរឹង៖ ត្រូវតែ Login រួចរាល់ និងត្រូវតែជា Superadmin ប៉ុណ្ណោះ
    if request.user.is_authenticated and request.user.is_superuser:
        accessed = True  # អនុញ្ញាតឱ្យចូលមើល
    else:
        # បើមិនមែនជា Superadmin ទេ គឺត្រូវទាត់ពួកគេទៅកាន់ទំព័រ Login វិញភ្លាម
        messages.error(request, "សូមចូលប្រើប្រាស់គណនី Superadmin ជាមុនសិន ដើម្បីមើលទំព័រនេះ!")
        return redirect('login')

    all_users = User.objects.all()
    
    return render(request, 'user_list.html', {
        'users': all_users,
        'accessed': accessed,
        'error': error
    })

# ==========================================================
# 7. Logic សម្រាប់ការបញ្ជាទិញទំនិញ (Place Order)
# ==========================================================
@login_required(login_url='login') # បើមិនទាន់ Login ទេ វានឹងរុញទៅទំព័រ Login ស្វ័យប្រវត្ត
def place_order(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        # ទាញយកទិន្នន័យផលិតផល
        product = get_object_or_404(Product, id=product_id)
        total_price = product.price * quantity
        
        # ១. បង្កើត Order មេ
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status='Pending'
        )
        
        # ២. បង្កើត មុខទំនិញកូន
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )
        
        # ពេលជោគជ័យ បញ្ជូនទៅកាន់ទំព័រ Check វិក្កយបត្រ (Order Detail)
        return redirect('order_detail', order_id=order.id)
        
    return redirect('index')

# ==========================================================
# 8. Logic សម្រាប់បង្ហាញព័ត៌មានលម្អិតនៃវិក្កយបត្រ (Order Detail)
# ==========================================================
@login_required(login_url='login')
def order_detail(request, order_id):
    # ទាញយកទិន្នន័យ Order របស់ User ដែលកំពុង Login បើរកមិនឃើញឱ្យចេញ Error 404
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {
        'order': order
    })

# ==========================================================
# 9. Logic សម្រាប់ Admin ចូលមើលរាល់ការកុម្ម៉ង់ទាំងអស់ (Custom Admin View)
# ==========================================================
@login_required(login_url='login')
def admin_orders_view(request):
    # ធានាថាមានតែ Superuser/Admin ប៉ុណ្ណោះទើបអាចមើលទំព័រនេះបាន
    if not request.user.is_superuser:
        messages.error(request, "អ្នកគ្មានសិទ្ធិចូលមើលទំព័រនេះទេ!")
        return redirect('index')
        
    # ទាញយក Order ទាំងអស់ដោយតម្រៀបពីថ្មីបំផុតមកមុន
    all_orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_orders.html', {
        'orders': all_orders
    })

# ==========================================================
# 10. Logic សម្រាប់ Admin ចុចយល់ព្រមទទួលការកុម្ម៉ង់ (Accept Order)
# ==========================================================
@login_required(login_url='login')
def admin_accept_order(request, order_id):
    if not request.user.is_superuser:
        return redirect('index')
    
    order = get_object_or_404(Order, id=order_id)
    order.status = 'Accepted' # ផ្លាស់ប្តូរស្ថានភាពទៅជាបានទទួលយក
    order.save()
    messages.success(request, f"បានទទួលយកការកម្ម៉ង់ #{order.id} រួចរាល់!")
    return redirect('admin_orders')

# ==========================================================
# 11. Logic សម្រាប់ Admin បញ្ចប់ការកុម្ម៉ង់ពេលភ្ញៀវបង់លុយរួច (Complete Order)
# ==========================================================
@login_required(login_url='login')
def admin_complete_order(request, order_id):
    if not request.user.is_superuser:
        return redirect('index')
        
    order = get_object_or_404(Order, id=order_id)
    order.status = 'Completed' # ផ្លាស់ប្តូរស្ថានភាពទៅជាជោគជ័យ (ពេលភ្ញៀវបង់លុយរួច)
    order.save()
    messages.success(request, f"ការកម្ម៉ង់ #{order.id} ត្រូវបានបញ្ចប់ជាស្ថាពរ!")
    return redirect('admin_orders')

@login_required(login_url='login')
def my_orders_view(request):
    # ទាញយក Order ទាំងអស់ដែលជារបស់ភ្ញៀវម្នាក់នេះ (តម្រៀបពីថ្មីទៅចាស់)
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {
        'orders': user_orders
    })