from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# ==========================================================
# 1. Logic បង្ហាញទំព័រដើមទិញទំនិញ (Index / Products)
# ==========================================================
def index(request):
    products = [
        {"name": "អង្ករផ្ការំដួលជើងភ្នំ", "price": "15$", "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500"},
        {"name": "ម្រេចកំពតធម្មជាតិ", "price": "8$", "image": "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?w=500"},
        {"name": "ស្ករត្នោតខេត្តកំពង់ស្ពឺ", "price": "5$", "image": "https://images.unsplash.com/photo-1608686207856-001b95cf60ca?w=500"},
    ]
    return render(request, 'index.html', {'products': products})

# ==========================================================
# 2. Logic សម្រាប់ចុះឈ្មោះអ្នកប្រើប្រាស់ (Register)
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
# 3. Logic សម្រាប់ចូលប្រើប្រាស់ប្រព័ន្ធ (Login)
# ==========================================================
def login_view(request):
    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        
        # ប្រើប្រាស់ authenticate ដែលបាន import ត្រឹមត្រូវពីខាងលើ (ដោះស្រាយ error image_0b177f.png)
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            login(request, user)
            # បើជា Superadmin ឱ្យរត់ទៅទំព័រ check-users ភ្លាម
            if user.is_superuser:
                return redirect('user_list')
            return redirect('index') 
        else:
            messages.error(request, "ឈ្មោះអ្នកប្រើប្រាស់ ឬលេខសម្ងាត់មិនត្រឹមត្រូវទេ!")
            
    return render(request, 'login.html')

# ==========================================================
# 4. Logic សម្រាប់ចាកចេញពីប្រព័ន្ធ (Logout)
# ==========================================================
def logout_view(request):
    logout(request) 
    return redirect('login') 

# ==========================================================
# 5. Logic មើលបញ្ជីឈ្មោះ User (ត្រូវ Login ជា Superadmin ជាមុនសិន)
# ==========================================================
def user_list_view(request):
    error = None
    
    # លក្ខខណ្ឌតឹងរឹង៖ ត្រូវតែ Login រួចរាល់ និងត្រូវតែជា Superadmin ប៉ុណ្ណោះ
    if request.user.is_authenticated and request.user.is_superuser:
        accessed = True  # អនុញ្ញាតឱ្យចូលមើល
    else:
        # បើមិនទាន់ Login ឬមិនមែនជា Superadmin ទេ គឺត្រូវទាត់ពួកគេទៅកាន់ទំព័រ Login វិញភ្លាម
        messages.error(request, "សូមចូលប្រើប្រាស់គណនី Superadmin ជាមុនសិន ដើម្បីមើលទំព័រនេះ!")
        return redirect('login')

    all_users = User.objects.all()
    
    return render(request, 'user_list.html', {
        'users': all_users,
        'accessed': accessed,
        'error': error
    })
