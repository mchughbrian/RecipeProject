from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.

# Django's built-in render function and our Recipe model are imported
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Recipe, MealPlan, MealDay
from .forms import RecipeForm, MealDayForm
from .forms import MealPlanForm
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

    # Check if sortField parameter is present
    #sort_field = request.GET.get('sortField')
    #if sort_field:
    #    recipes = recipes.order_by(sort_field)

    #return render(request, 'recipes/home.html', {'recipes': recipes})


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


def add_recipe(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            new_recipe = form.save(commit=False)
            new_recipe.user = request.user
            new_recipe.save()
            return redirect('home')
    else:
        form = RecipeForm()

    return render(request, 'recipes/add_recipe.html', {'form': form})


# This function represents the view for deleting a recipe.
# 'login_required' decorator is used to ensure that only logged-in users can access this view.
@login_required
def delete_recipe(request, recipe_id):
    # Retrieve the recipe by its ID.
    recipe = Recipe.objects.get(id=recipe_id)

    # Check if the logged-in user is the one who added the recipe.
    if recipe.user == request.user:
        # If so, delete the recipe.
        recipe.delete()

    # After deleting the recipe (or if the user didn't have permission to delete it), redirect the user to the homepage.
    return redirect('home')


# Define a view function named 'recipe' which takes a request and recipe_id as arguments
def recipe(request, recipe_id):
    # Try to get the Recipe object with the provided recipe_id.
    # If the object does not exist, the function will return a 404 response immediately.
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    # If the method of the request is POST, it means that the delete button on the recipe page was clicked
    if request.method == 'POST':
        # Delete the recipe object from the database
        recipe.delete()

        # After deleting the recipe, redirect the user back to the homepage
        return redirect('home')

    # Create a context dictionary that includes the recipe object
    context = {'recipe': recipe}

    # Render the 'RecipeArchive/recipe.html' template, and pass in the context dictionary.
    # This will make the recipe data available in the template.
    return render(request, 'recipes/recipe.html', context)


def profile(request):
    # This is just a simple example. You can customize this view according to your needs.
    return render(request, 'registration/profile.html')


def edit_recipe(request, id):
    # Get the Recipe instance with the given ID. If no such instance exists,
    # the get_object_or_404 function will automatically render a 404 response.
    recipe = get_object_or_404(Recipe, id=id)

    # If the request method is POST, this means that the user has submitted the form.
    if request.method == "POST":
        # Create a form instance and populate it with data from the request and
        # files (uploaded images), binding it to the recipe instance.
        # If the form is valid, Django will automatically update the recipe instance.
        form = RecipeForm(request.POST, request.FILES, instance=recipe)

        # Check if the form is valid.
        if form.is_valid():
            # Save the changes made to the recipe instance.
            form.save()

            # After saving the changes, redirect the user to the home page.
            return redirect('home')

    # If the request method is not POST, this means the user has navigated to the page
    # but has not submitted the form. In this case, we want to display the form
    # populated with the current data of the recipe instance.
    else:
        form = RecipeForm(instance=recipe)

    # Render the 'edit_recipe.html' template with the form as context.
    return render(request, 'recipes/edit_recipe.html', {'form': form})


#def create_meal_plan(request):
#    if request.method == 'POST':
#        form = MealPlanForm(request.POST)
#        if form.is_valid():
#            # process the data in form.cleaned_data as required
#            # redirect to a new URL:
#            return HttpResponseRedirect('/recipes/create_mealday.html')
#    else:
#        form = MealPlanForm()
#
#    return render(request, 'recipes/create_meal_plan.html', {'form': form})


'''def create_mealday(request):
    # retrieve the mealplan created by the current user and sorted by the creation date in descending order
    # so the first one would be the latest mealplan created
    mealplan = MealPlan.objects.filter(user=request.user).order_by('-created_date').first()

    # if the request method is POST
    if request.method == 'POST':
        # initialize the MealDayForm with POST data and some extra arguments
        meals = [mealplan.breakfast, mealplan.lunch, mealplan.dinner]
        form = MealDayForm(request.POST, user=request.user, days=mealplan.days, meals=meals) #, meals=mealplan.meals.split(','))

        # if the form is valid
        if form.is_valid():
            # for each field in the form
            for field, value in form.cleaned_data.items():
                # split the field name by '_' to get the day and meal
                days, meal = field.split('_')[1:3]
                # create a new MealDay instance
                MealDay.objects.create(
                    meal_plan=mealplan,  # assign the meal plan
                    days=int(days),  # convert the day to an integer
                    meal_type=meal,  # assign the meal type
                    recipe=value  # assign the selected recipe
                )
            # redirect to a new page (replace 'home' with wherever you want to redirect)
            return redirect('home')
    # if the request method is not POST, initialize the form without any data
    else:
        meals = [mealplan.breakfast, mealplan.lunch, mealplan.dinner]
        form = MealDayForm(request.POST, user=request.user, days=mealplan.days, meals=meals)  # , meals=mealplan.meals.split(','))

    # render the template with the form
    return render(request, 'recipes/create_mealday.html', {'form': form})'''


def create_mealday(request, mealplan_id):
    mealplan = get_object_or_404(MealPlan, id=mealplan_id)
    days = mealplan.days
    meals = {
        'breakfast': mealplan.breakfast,
        'lunch': mealplan.lunch,
        'dinner': mealplan.dinner,
    }
    if request.method == 'POST':
        form = MealDayForm(request.POST, user=request.user, days=days, meals=meals)
        if form.is_valid():
            # process the form and redirect as needed
            return redirect('mealplan_detail', mealplan_id=mealplan.id)
    else:
        form = MealDayForm(user=request.user, days=days, meals=meals)

    return render(request, 'recipes/create_mealday.html', {'form': form})


def create_mealplan(request):
    # if the request method is POST
    if request.method == 'POST':
        # initialize the MealPlanForm with POST data
        form = MealPlanForm(request.POST)

        # if the form is valid
        if form.is_valid():
            # save the form but don't commit to database yet
            mealplan = form.save(commit=False)
            # assign the current user to the mealplan's user
            mealplan.user = request.user
            # save the mealplan to the database
            mealplan.save()

            days = form.cleaned_data['days']
            meals = []  # Here you need to get the list of meals based on user input

            # redirect to the create_mealdays view with the meal plan id as a parameter
            return redirect('create_mealday', mealplan_id=mealplan.id)

    # if the request method is not POST, initialize the form without any data
    else:
        form = MealPlanForm()

    # render the template with the form
    return render(request, 'recipes/create_mealplan.html', {'form': form})


def mealplan_detail(request, mealplan_id):
    # Retrieve the MealPlan object using the provided mealplan_id
    mealplan = get_object_or_404(MealPlan, id=mealplan_id)

    # Render the meal plan details template with the mealplan object
    return render(request, 'recipes/mealplan_detail.html', {'mealplan': mealplan})
    #return redirect('recipes/mealplan_detail', mealplan_id=mealplan.id)
