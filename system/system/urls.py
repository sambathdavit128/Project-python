"""
URL configuration for system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # បានថែមសម្រាប់ទាញយកការកំណត់ពី settings.py
from django.conf.urls.static import static  # បានថែមសម្រាប់បង្កើតផ្លូវឯកសារ Static/Media

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('adminsystem.urls')),
]

# បន្ថែមបន្ទាត់នេះដើម្បីឱ្យ Django អនុញ្ញាតឱ្យទាញរូបភាពពី folder media មកបង្ហាញលើ Browser
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)