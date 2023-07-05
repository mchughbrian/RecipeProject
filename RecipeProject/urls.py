"""
URL configuration for RecipeProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

#urlpatterns = [
#   path('admin/', admin.site.urls),
#]

# Django's built-in path function and our views are imported
from django.urls import path
from django.contrib.auth.views import LoginView
from RecipeArchive import views

# URL patterns are defined for our app
urlpatterns = [
    # An empty path ('') is mapped to our home view.
    # This means that when a user navigates to the root URL of our app, the home view will be used to handle the request.
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("register/", views.register, name="register"),
    path('recipes/', views.home, name='home'),
]

