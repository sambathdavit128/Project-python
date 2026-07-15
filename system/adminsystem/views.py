from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone  # បន្ថែមសម្រាប់គណនាម៉ោង Cancel Order
from datetime import timedelta     # បន្ថែមសម្រាប់កំណត់រយៈពេល ៣ នាទី

# ទាញយក class models ទាំងអស់ចេញពី models.py មកប្រើជាមួយគ្នា
from .models import Category, Shop, Product, Order, OrderItem 


# ==========================================================
# 0. Context Processor សម្រាប់រាប់ចំនួន Order មិនទាន់បញ្ចប់ (Active Orders Count)
# ==========================================================
def active_orders_count(request):
    """
    អនុគមន៍នេះប្រើសម្រាប់រាប់ចំនួនកុម្ម៉ង់ដែលកំពុងដំណើរការ (Pending ឬ Accepted)
    ដើម្បីបង្ហាញលេខនៅលើរូបកន្ត្រក Navbar គ្រប់ទំព័រស្វ័យប្រវត្ត។
    """
    if request.user.is_authenticated:
        count = Order.objects.filter(
            user=request.user, 
            status__in=['Pending', 'Accepted']
        ).count()
        return {'active_orders_count': count}
    return {'active_orders_count': 0}


# ==========================================================
# 1. Logic បង្ហាញទំព័រដើមទិញទំនិញ (Index / Shops & Products) [បានកែប្រែបន្ថែមការ Filter Discount]
# ==========================================================
def index(request):
    # ១. ទាញយកទិន្នន័យ "ហាងទាំងអស់" និង "ផលិតផលទាំងអស់" ចេញពី Database 
    shops = Shop.objects.all()
    products = Product.objects.all()
    
    # ២. ឆែកមើលថាតើ User បានចុចលើប៊ូតុង 'ប្រូម៉ូសិន (Deals)' ដែលបោះតម្លៃ ?discount_only=true មកឬអត់
    discount_only = request.GET.get('discount_only')
    
    if discount_only == 'true':
        # ចម្រាញ់យកតែផលិតផលណាដែលមានភាគរយបញ្ចុះតម្លៃ (discount) ធំជាង 0%
        # (ចំណាំ៖ ប្រសិនបើក្នុង models.py របស់ប្អូនប្រើឈ្មោះ field ផ្សេង ដូចជា discount_percentage សូមប្ដូរឈ្មោះត្រង់នេះចេញ)
        products = products.filter(discount__gt=0)
    
    return render(request, 'index.html', {
        'shops': shops,
        'products': products,
        'discount_only': discount_only  # បោះទៅ HTML វិញដើម្បីងាយស្រួលដឹងថាកំពុងបង្ហាញតែទំនិញ Discount
    })


# ==========================================================
# 2. View សម្រាប់បង្ហាញព័ត៌មានលម្អិត និងផលិតផលក្នុងហាងនីមួយៗ (Shop Detail)
# ==========================================================
def shop_detail(request, shop_id):
    # 1. ទទាញយកទិន្នន័យហាងណាដែលមាន id ស្មើនឹង shop_id បើរកមិនឃើញឱ្យចេញទំព័រ Error 404
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
# 7. Logic សម្រាប់ការបញ្ជាទិញទំនិញ (Place Order) -> [បានកែប្រែគណនាតាមតម្លៃ Discount]
# ==========================================================
@login_required(login_url='login') # បើមិនទាន់ Login ទេ វានឹងរុញទៅទំព័រ Login ស្វ័យប្រវត្ត
def place_order(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        # ចាប់យកទិន្នន័យលេខទូរស័ព្ទ និងអាសយដ្ឋានពី Form
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # ឆែកលក្ខខណ្ឌបើអតិថិជនមិនបានបំពេញព័ត៌មានទាំងពីរនេះ
        if not phone or not address:
            messages.error(request, "សូមបំពេញលេខទំនាក់ទំនង និងអាសយដ្ឋានបច្ចុប្បន្នរបស់អ្នក!")
            return redirect('shop_detail', shop_id=Product.objects.get(id=product_id).shop.id)

        # ទាញយកទិន្នន័យផលិតផល
        product = get_object_or_404(Product, id=product_id)
        
        # 👑 ចំណុចកែប្រែ៖ ប្រើប្រាស់ final_price (តម្លៃបញ្ចុះរួច) ជំនួសឱ្យ price ធម្មតា
        actual_price = product.final_price
        total_price = actual_price * quantity
        
        # ១. បង្កើត Order មេ (ដោយរក្សាទុកទាំង phone និង address)
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status='Pending',
            phone=phone,
            address=address
        )
        
        # ២. បង្កើត មុខទំនិញកូន (រក្សាទុកតម្លៃលក់ជាក់ស្តែង actual_price ទៅក្នុង DB)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=actual_price
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


# ==========================================================
# 12. Logic សម្រាប់ Customer ឆែកមើលរាល់ប្រវត្តិកុម្ម៉ង់ទាំងអស់ (My Orders)
# ==========================================================
@login_required(login_url='login')
def my_orders_view(request):
    # ទាញយកតែការកុម្ម៉ង់របស់អតិថិជនដែលកំពុង Log in និងតម្រៀបពីថ្មីទៅចាស់ (-id)
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'my_orders.html', {
        'orders': orders
    })


# ==========================================================
# 13. Logic សម្រាប់ Customer បោះបង់ការបញ្ជាទិញក្នុងរយះពេល ៣នាទី (Cancel Order)
# ==========================================================
@login_required(login_url='login')
def cancel_order(request, order_id):
    """
    មុខងារអនុញ្ញាតឱ្យអតិថិជនលុប ឬបោះបង់ការបញ្ជាទិញវិញ 
    ក្នុងករណីមិនទាន់ហួសរយៈពេល ៣ នាទី គិតចាប់ពីម៉ោងកុម្ម៉ង់។
    """
    # ទាញយក Order របស់អតិថិជនដែលកំពុង Login
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # កំណត់រយៈពេលផុតកំណត់ (៣ នាទី បូកបន្ថែមលើម៉ោងបង្កើត Order ក្នុង database)
    expiration_time = order.created_at + timedelta(minutes=3)
    
    # ពិនិត្យមើលលក្ខខណ្ឌម៉ោងបច្ចុប្បន្ន ធៀបនឹងម៉ោងផុតកំណត់
    if timezone.now() > expiration_time:
        messages.error(request, "ការកុម្ម៉ង់នេះមិនអាចបោះបង់បានទេ ព្រោះហួសរយៈពេល ៣ នាទីហើយ!")
        return redirect('my_orders')
    
    # លុប Order នេះចេញពីប្រព័ន្ធ
    order.delete()
    messages.success(request, "ការបញ្ជាទិញរបស់អ្នកត្រូវបានបោះបង់ដោយជោគជ័យ!")
    
    return redirect('my_orders')


# ==========================================================
# 14. Logic សម្រាប់ Admin បដិសេធ ឬបោះបង់ការកុម្ម៉ង់ (Admin Cancel Order)
# ==========================================================
@login_required(login_url='login')
def admin_cancel_order(request, order_id):
    """
    មុខងារអនុញ្ញាតឱ្យ Admin បដិសេធ ឬបោះបង់ (Cancel) Order របស់ភ្ញៀវចោលវិញ
    ដោយប្តូរ status ទៅជា 'Cancelled'។
    """
    if not request.user.is_superuser:
        return redirect('index')
        
    order = get_object_or_404(Order, id=order_id)
    order.status = 'Cancelled' # ផ្លាស់ប្តូរស្ថានភាពទៅជា Cancelled
    order.save()
    messages.success(request, f"ការកម្ម៉ង់ #{order.id} ត្រូវបានបោះបង់ (Cancelled) ដោយជោគជ័យ!")
    return redirect('admin_orders')


# ==========================================================
# 15. Logic សម្រាប់បង្ហាញទំព័រអំពីយើង (About Us)
# ==========================================================
def about_us(request):
    """
    បង្ហាញទំព័រ About Us ដែលមានព័ត៌មានពីសមាជិកក្រុមទាំងអស់។
    """
    return render(request, 'about.html')