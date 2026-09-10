"""
URL configuration for slappersnsizzlers_v1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    # include() splices accounts/urls.py in under this prefix — Django strips 'accounts/' off the path and hands the remainder to the accounts app to match; keeps each app's routes self-contained
    path('accounts/', include('accounts.urls')),
    # /menu/ prefix for the menu app — base.html already links to /menu/, and 'menu.index' is the post-signup destination in accounts/views.py
    path('menu/', include('menu.urls')),
    # /cart/ prefix — the exact path base.html's cart icon has pointed at since day one; the icon stops 404ing the moment this line exists
    path('cart/', include('cart.urls')),
    # /orders/ — the last of the four paths base.html promised on day one; with this line the whole navbar finally resolves
    path('orders/', include('orders.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
