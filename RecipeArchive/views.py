import os
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape
from .models import Recipe, MealPlan, MealDay, MealDayModelForm
from .forms import RecipeForm, MealDayForm, RecipeSearchForm
from .forms import MealPlanForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
import requests
from django.conf import settings
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileForm
from .models import Profile
from django.contrib.auth import logout
from .forms import CustomUserCreationForm
from openai import OpenAI
import os


# A view is defined to handle requests to the homepage
@login_required
def home(request):
    # The view checks if the user is authenticated
    if request.user.is_authenticated:
        # Start with all recipes excluding special categories
        recipes = Recipe.objects.exclude(name__in=["Takeout", "N/A"])
        user_profile = request.user.profile

        # Filter by meal type if specified
        meal_type = request.GET.get('meal_type', '')
        if meal_type and meal_type != 'All':
            recipes = recipes.filter(meal_type=meal_type, user=request.user)  # Filter recipes based on meal type
        else:
            recipes = recipes.filter(user=request.user)  # Keep excluding special categories

        # Filter by rating if specified
        rating = request.GET.get('rating', '')
        if rating:
            recipes = recipes.filter(rating=rating)

        context = {
            'recipes': recipes,
            'meal_type': meal_type,
            'user_profile': user_profile,
            # ... other context variables ...
        }

        # It then renders the 'recipes/home.html' template, passing in the list of recipes as context
        return render(request, 'recipes/home.html', context)

    # If the user is not authenticated, it renders the 'recipes/login.html' template
    else:
        return redirect('login')

    # Check if sortField parameter is present
    # sort_field = request.GET.get('sortField')
    # if sort_field:
    #    recipes = recipes.order_by(sort_field)

    # return render(request, 'recipes/home.html', {'recipes': recipes})


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a profile for the new user
            try:
                Profile.objects.get_or_create(user=user)
            except Exception as e:
                print("Error creating profile:", e)
            # Log the user in and redirect to the home page
            login(request, user)
            return redirect("home")  # Redirect to the home page or another appropriate page
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required()
def add_recipe(request):
    if request.method == "POST":
        print(request.POST)  # Print the POST data
        form = RecipeForm(request.POST, request.FILES)

        if form.is_valid():
            new_recipe = form.save(commit=False)
            new_recipe.user = request.user

            # Check if an image URL is provided in the POST data
            image_url = form.cleaned_data.get('image_url')
            print("Image URL:", image_url)
            #if image_url:
                # If an image URL is provided, use it
             #   new_recipe.image_url = image_url  # Assign to 'image_url' field
            if image_url and image_url != 'None':
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Count the number of recipes with image_urls for this user
                    image_count = Recipe.objects.filter(user=request.user, image_url__isnull=False).count()

                    # Generate a new filename
                    image_name = f"ImageGen_{image_count + 1}.jpg"

                    # Save the image to the model's ImageField
                    new_recipe.image.save(image_name, ContentFile(response.content), save=False)

            new_recipe.save()
            return redirect('home')
        else:
            print(form.errors)
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


@login_required()
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
        form.fields.pop('image_url', None)  # Exclude the image_url field

        # Check if the form is valid.
        if form.is_valid():
            # Save the changes made to the recipe instance.
            form.save()

            # After saving the changes, redirect the user to the home page.
            return redirect('home')
        else:
            print(form.errors)
    # If the request method is not POST, this means the user has navigated to the page
    # but has not submitted the form. In this case, we want to display the form
    # populated with the current data of the recipe instance.
    else:
        form = RecipeForm(instance=recipe)

    # Render the 'edit_recipe.html' template with the form as context.
    return render(request, 'recipes/edit_recipe.html', {'form': form})


@login_required()
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
            for i in range(1, days + 1):
                for meal_type in ['breakfast', 'lunch', 'dinner']:
                    if meals[meal_type]:  # Only if the boolean for the meal type is TRUE
                        recipe = form.cleaned_data.get(f"{meal_type}_{i}")
                        if recipe:
                            MealDay.objects.create(
                                meal_plan=mealplan,
                                day=i,
                                meal_type=meal_type,
                                recipe=recipe
                            )
            return redirect('mealplan_detail', mealplan_id=mealplan.id)
    else:
        form = MealDayForm(user=request.user, days=days, meals=meals)

    return render(request, 'recipes/create_mealday.html', {'form': form})


@login_required()
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


@login_required()
def mealplan_detail(request, mealplan_id):
    mealplan = get_object_or_404(MealPlan, id=mealplan_id)
    meal_days = MealDay.objects.filter(meal_plan=mealplan).order_by('day')

    # Group meals by day
    grouped_meals = {}
    for meal_day in meal_days:
        day = meal_day.day
        if day not in grouped_meals:
            grouped_meals[day] = []
        grouped_meals[day].append(meal_day)

    context = {
        'mealplan': mealplan,
        'grouped_meals': grouped_meals
    }
    return render(request, 'recipes/mealplan_detail.html', context)


@login_required()
def view_mealplans(request):
    # get all the mealplans of the current user and order by 'updated' field in descending order
    mealplans = MealPlan.objects.filter(user=request.user).order_by('-updated')
    return render(request, 'recipes/view_mealplans.html', {'mealplans': mealplans})


@login_required()
def edit_mealplan(request, mealplan_id):
    mealplan = get_object_or_404(MealPlan, id=mealplan_id)
    mealday_instances = MealDay.objects.filter(meal_plan=mealplan)

    if request.method == 'POST':
        forms = [MealDayModelForm(request.POST, prefix=str(md.id), instance=md) for md in mealday_instances]
        if all(form.is_valid() for form in forms):
            for form in forms:
                form.save()
            return redirect('mealplan_detail', mealplan_id=mealplan.id)
    else:
        forms = [MealDayModelForm(prefix=str(md.id), instance=md) for md in mealday_instances]

    # Combine forms and mealday_instances for easy iteration in the template
    forms_mealdays = zip(forms, mealday_instances)

    return render(request, 'recipes/edit_mealplan.html', {'forms_mealdays': forms_mealdays, 'mealplan': mealplan})


@login_required()
def delete_mealplan(request, mealplan_id):
    # get the mealplan or 404 if not found
    mealplan = get_object_or_404(MealPlan, id=mealplan_id)

    # check if the logged-in user is the owner of the mealplan
    if request.user != mealplan.user:
        return HttpResponseForbidden()

    # if this is a POST request, delete the mealplan
    if request.method == 'POST':
        mealplan.delete()
        messages.success(request, 'Meal plan deleted successfully')
        return redirect('view_mealplans')  # assuming 'mealplans' is the URL where you list all meal plans

    # if not a POST request, render the confirm delete page
    return render(request, 'recipes/confirm_delete.html', {'mealplan': mealplan})

@login_required()
def get_available_recipes_for_user(user):
    # Get recipes owned by the user
    user_recipes = Recipe.objects.filter(user=user)

    # Get special recipes
    special_recipes = Recipe.objects.filter(user__username='default_user')

    # Combine and return
    return user_recipes | special_recipes


@login_required()
def download_mealplan(request, mealplan_id):
    mealplan = get_object_or_404(MealPlan, id=mealplan_id)
    mealday_instances = MealDay.objects.filter(meal_plan=mealplan)

    # Create the text content
    content = f"Meal Plan: {mealplan.name}\n"
    content += "===================================\n"

    for mealday in mealday_instances:
        content += f"Day {mealday.day} - {mealday.get_meal_type_display()}: {mealday.recipe}\n"

    # Create the HttpResponse object with the text content,
    # and a Content-Disposition header forcing a filename
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=mealplan.txt'
    return response


'''def discover(request):
    recipes = []
    form = RecipeSearchForm()
    error_message = None
    number_of_results = 10  # Specify the number of results you want

    if request.method == 'POST':
        form = RecipeSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            API_ENDPOINT = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/complexSearch"
            API_KEY = settings.API_KEY
            API_HOST = settings.API_HOST

            try:
                response = requests.get(API_ENDPOINT,
                                        headers= {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": API_HOST},
                                        params={"query": query, "number": number_of_results})
                if response.status_code == 200:
                    data = response.json()
                    recipes = data.get('results', [])
                else:
                    error_message = "An error occurred while fetching recipes."
            except requests.RequestException:
                error_message = "Failed to connect to the recipe service."

    return render(request, 'recipes/discover.html', {'form': form, 'recipes': recipes, 'error_message': error_message})
'''


@login_required
def my_profile(request):
    if request.method == 'POST':
        user_form = UserChangeForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')

        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('my_profile')  # Redirect to a confirmation page or back to the profile page

        # Redirect to some page upon success
        return redirect('my_profile')

    else:
        user_form = UserChangeForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'password_form': password_form,
        'profile_form': profile_form
    }
    return render(request, 'recipes/my_profile.html', context)


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to the home page if logged in
    return render(request, 'registration/landing_page.html')  # Show the landing page otherwise


def privacy_policy(request):
    return render(request, 'registration/privacy_policy.html')


def terms_of_use(request):
    return render(request, 'registration/terms_of_use.html')


def generate_image(request):
    # Check if the request is a POST request
    user_profile = get_object_or_404(Profile, user=request.user)

    if user_profile.generated_images_count >= 5:
        # Return a response indicating the limit has been reached
        return JsonResponse({'error': 'Image generation limit reached'}, status=403)

    if request.method == 'POST':
        # Retrieve the user's prompt from the POST data
        prompt = request.POST.get('prompt')
        print(prompt)
        # Initialize the OpenAI client with your API key
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        # Call the OpenAI API to generate an image based on the prompt
        response = client.images.generate(
            model="dall-e-3",  # Specify the model to use
            prompt=prompt,     # The user's text prompt
            size="1024x1024",  # The size of the generated image
            quality="standard",# The quality of the image
            n=1,               # Number of images to generate
        )

        # Extract the URL of the generated image from the response
        image_url = response.data[0].url

        #keep track of image generation count
        user_profile.generated_images_count += 1
        user_profile.save()

        # Return the image URL in a JSON response
        return JsonResponse({'image_url': image_url})

    # If the request is not a POST request, return an error
    return JsonResponse({'error': 'Invalid request'}, status=400)