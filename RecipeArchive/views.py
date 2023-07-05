from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render

# Create your views here.

# Django's built-in render function and our Recipe model are imported
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Recipe
from django.contrib.auth.decorators import login_required

# A view is defined to handle requests to the homepage
def home(request):
    # The view checks if the user is authenticated
    if request.user.is_authenticated:
        # If the user is authenticated, it queries the database for all recipes added by this user
        recipes = Recipe.objects.filter(user=request.user)

        # It then renders the 'recipes/home.html' template, passing in the list of recipes as context
        return render(request, 'recipes/home.html', {'recipes': recipes})

    # If the user is not authenticated, it renders the 'recipes/login.html' template
    else:
        return redirect('login')

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")  # Or specify where you want to redirect the user after successful registration
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


