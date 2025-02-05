"""navigate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from django.urls import include
from oauth2_provider import urls as oauth2_urls

urlpatterns = [
    path('navigate/admin/', admin.site.urls),
    path('navigate/farms/', include('v1.farms.urls')),
    path('navigate/supply-chains/', include('v1.supply_chains.urls')),
    path('navigate/dashboard/', include('v1.dashboard.urls')),
    path('navigate/oauth/', include(oauth2_urls)),
]
