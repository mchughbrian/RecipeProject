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
from django.contrib.auth.views import LoginView
from RecipeArchive import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from RecipeArchive.views import subscription_page, subscription_manage, cancel_subscription, payment_success, \
    update_email, change_password

# URL patterns are defined for our app
urlpatterns = [
    # An empty path ('') is mapped to our home view.
    # This means that when a user navigates to the root URL of our app, the home view will be used to handle the request.
    path('', views.landing_page, name='landing_page'),
    path('home/', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("register/", views.register, name="register"),
    path('recipes/', views.home, name='home'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('add-recipe/', views.add_recipe, name='add_recipe'),
    path('delete/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
    path('recipe/<int:recipe_id>/', views.recipe, name='recipe'),
    path('profile/', views.profile, name='profile'),
    path('edit-recipe/<int:id>/', views.edit_recipe, name='edit_recipe'),
    path('create_mealday/', views.create_mealday, name='create_mealday'),
    path('create-mealplan/', views.create_mealplan, name='create_mealplan'),
    path('create-mealday/<int:mealplan_id>/', views.create_mealday, name='create_mealday'),
    path('mealplan/<int:mealplan_id>/', views.mealplan_detail, name='mealplan_detail'),
    path('view-mealplans/', views.view_mealplans, name='view_mealplans'),
    path('edit-mealplan/<int:mealplan_id>/', views.edit_mealplan, name='edit_mealplan'),
    path('mealplan/<int:mealplan_id>/delete/', views.delete_mealplan, name='delete_mealplan'),
    path('download_mealplan/<int:mealplan_id>/', views.download_mealplan, name='download_mealplan'),
    #path('discover/', views.discover, name='discover'),
    path('my_profile', views.my_profile, name='my_profile'),
    path('registration/', include('django.contrib.auth.urls')),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-use/', views.terms_of_use, name='terms_of_use'),
    path('generate-image/', views.generate_image, name='generate-image'),
    path('subscription-page/', subscription_page, name='subscription-page'),
    path('subscription_manage/', subscription_manage, name='subscription_manage'),
    path('cancel-subscription/', cancel_subscription, name='cancel_subscription'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('cancel/', views.payment_cancelled, name='payment_cancelled'),
    path('success/', payment_success, name='payment_success'),
    path('update_email/', update_email, name='update_email'),
    #path('accounts/', include('django.contrib.auth.urls')),
    path('change_password/', change_password, name='change_password'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),

] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

