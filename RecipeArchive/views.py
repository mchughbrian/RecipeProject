import os

import boto3
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape
from django.views.decorators.http import require_POST
from django.core.files import File
from .emails import send_welcome_email, send_subscribe_email, send_cancel_email, send_profile_email
from .signals import subscription_created
from .management.commands.assign_starter_recipes import assign_starter_recipes
from .models import Recipe, MealPlan, MealDay, MealDayModelForm
from .forms import RecipeForm, MealDayForm, RecipeSearchForm, EmailUpdateForm, CustomPasswordChangeForm
from .forms import MealPlanForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
import requests
from django.conf import settings
import stripe
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileForm
from .models import Profile
from django.contrib.auth import logout
from .forms import CustomUserCreationForm
from openai import OpenAI
import os
from django.core.exceptions import PermissionDenied
from datetime import datetime
stripe.api_key = settings.STRIPE_SECRET_KEY


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
                messages.error(request, f"Error creating profile: {e}")

            # Attempt to create a Stripe customer for the new user
            try:
                create_stripe_customer(user)
            except Exception as e:
                print("Error creating Stripe customer:", e)

            # Send welcome email
            try:
                send_welcome_email(user)
            except Exception as e:
                print("Error sending welcome email:", e)
                # Optionally handle email errors, e.g., log them or notify an admin

            # Log the user in and redirect to the home page
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
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
            image = form.cleaned_data.get('image')
            #print("Image URL:", image_url)

            if not image and not image_url:
                # Specify the path to your default image
                default_image_path = f"{settings.STATIC_URL}images/default.png"
                # Open the default image
                response = requests.get(default_image_path)
                if response.status_code == 200:
                    # Create a ContentFile object from the downloaded image content
                    image_content = ContentFile(response.content)
                    # Save the image to the model's ImageField
                    new_recipe.image.save('default.png', image_content, save=True)
                else:
                    print(f"Failed to download the image.")
            elif image_url and image_url != 'None':
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
    # Retrieve the recipe by its ID and ensure ownership.
    recipe = get_object_or_404(Recipe, id=recipe_id, user=request.user)

    # If the recipe has an associated image file, delete the file using Django's storage backend
    if recipe.image:
        # This will handle the deletion using the configured storage backend (e.g., S3)
        recipe.image.delete(save=False)

    # Delete the recipe record from the database
    recipe.delete()

    # After deleting the recipe, redirect the user to the homepage.
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
        # Capture the current image path
        current_image_path = recipe.image.name if recipe.image else None
        current_image_url = recipe.image_url if recipe.image_url else None

        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        form.fields.pop('image_url', None)  # Exclude the image_url field
        if form.is_valid():
            # Check if the image was updated
            updated_recipe = form.save(commit=False)  # Save the form but don't commit to DB yet
            new_image_path = updated_recipe.image.name if updated_recipe.image else None
            image_url = form.cleaned_data.get('image_url')

            # Check if the image is cleared
            if not updated_recipe.image and not image_url:

                default_image_url = f"{settings.STATIC_URL}images/default.png"
                response = requests.get(default_image_url)

                if response.status_code == 200:
                    # Create a ContentFile object from the downloaded image content
                    image_content = ContentFile(response.content)

                    # Save the image to the recipe instance
                    updated_recipe.image.save('default.png', image_content, save=False)
                else:
                    print(f"Failed to download default image from {default_image_url}")

            elif current_image_path != new_image_path:
                # Delete the old image from S3 if it exists and is different from the new image
                if current_image_path:
                    try:
                        default_storage.delete(current_image_path)
                        print(f"Deleted old image {current_image_path} from S3.")
                    except Exception as e:
                        print(f"Error deleting old image {current_image_path} from S3: {e}")

            elif current_image_url != image_url and image_url is not None:
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Count the number of recipes with image_urls for this user
                    image_count = Recipe.objects.filter(user=request.user, image_url__isnull=False).count()

                    # Generate a new filename
                    image_name = f"ImageGen_{image_count + 1}.jpg"

                    # Save the image to the model's ImageField
                    updated_recipe.image.save(image_name, ContentFile(response.content), save=False)


            updated_recipe.save()  # Now commit the updates to the database
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = RecipeForm(instance=recipe)

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
        # messages.success(request, 'Meal plan deleted successfully')
        return redirect('view_mealplans')  # assuming 'mealplans' is the URL where you list all meal plans

    # if not a POST request, render the confirm delete page
    return render(request, 'recipes/confirm_delete.html', {'mealplan': mealplan})


def get_available_recipes_for_user(user):
    # Get recipes owned by the user
    user_recipes = Recipe.objects.filter(user=user).order_by('name')

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
        password_form = CustomPasswordChangeForm(request.user, request.POST)
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
        password_form = CustomPasswordChangeForm(request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    user_profile = request.user.profile
    generated_image_count = max(5 - user_profile.generated_images_count, 0)
    image_generations_remaining = 20-user_profile.image_generations_this_month

    context = {
        'user_form': user_form,
        'password_form': password_form,
        'profile_form': profile_form,
        'image_generations_remaining': image_generations_remaining,
        'generated_image_count': generated_image_count
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

    # Check if the user does not have a subscription and has reached the free limit
    if not user_profile.has_subscription and user_profile.generated_images_count >= 5:
        return JsonResponse({'error': 'Free image generation limit reached. Please subscribe for more.'}, status=403)

    # Check if the user has a subscription but has reached the monthly limit
    elif user_profile.has_subscription and user_profile.image_generations_this_month >= 20:
        return JsonResponse({'error': 'Monthly image generation limit reached.'}, status=403)

    # Proceed with image generation logic
    if request.method == 'POST':
        # Retrieve the user's prompt from the POST data
        prompt = request.POST.get('prompt')
        print(prompt)
        # Initialize the OpenAI client with your API key
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        # Call the OpenAI API to generate an image based on the prompt
        response = client.images.generate(
            model="dall-e-3",    # Specify the model to use
            prompt=prompt,       # The user's text prompt
            size="1024x1024",    # The size of the generated image
            quality="standard",  # The quality of the image
            n=1,                 # Number of images to generate
        )

        # Extract the URL of the generated image from the response
        image_url = response.data[0].url

        # Increment the appropriate image generation count
        if user_profile.has_subscription:
            user_profile.image_generations_this_month += 1
            user_profile.generated_images_count += 1
        else:
            user_profile.generated_images_count += 1

        user_profile.save()

        # Return the image URL in a JSON response
        return JsonResponse({'image_url': image_url})

    # If the request is not a POST request, return an error
    return JsonResponse({'error': 'Invalid request'}, status=400)


def subscription_page(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    user = request.user
    if not user.profile.stripe_customer_id:
        try:
            create_stripe_customer(user)
        except Exception as e:
            print("Error creating Stripe customer:", e)
            # Handle the error appropriately (e.g., show an error message to the user)

    # You can define your subscription plans or retrieve them from Stripe
    plans = [
        {"id": "Plan_1", "name": "Basic Plan", "price": 10},  # Example plan
        # Add more plans as needed
    ]

    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'plans': plans,
    }

    return render(request, 'registration/subscription_page.html', context)


stripe.api_key = settings.STRIPE_SECRET_KEY


def get_user_next_billing_date(user_profile):
    subscription_id = user_profile.stripe_subscription_id
    if not subscription_id:
        return "No Subscription Found"

    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        next_billing_date = datetime.fromtimestamp(
            subscription.current_period_end
        ).strftime('%B %d, %Y')  # Example format: "March 10, 2024"
        return f"{next_billing_date}"
    except Exception as e:
        print(e)
        return "Error retrieving subscription details"


def subscription_manage(request):
    profile = request.user.profile
    # Assuming you have fields like next_bill_date, price, and subscription_type in your Profile model
    # Call the function to get the next billing date
    next_bill_date = get_user_next_billing_date(profile)

    subscription_status = "Active" if profile.has_subscription else "Inactive"

    context = {
        'next_bill_date': next_bill_date,
        'price': '4.99',
        'current_subscription': subscription_status,
    }
    return render(request, 'registration/subscription_manage.html', context)


@require_POST  # Ensure this view only accepts POST requests
@login_required
def cancel_subscription(request):
    profile = request.user.profile

    if profile.stripe_subscription_id:
        try:
            subscription = stripe.Subscription.modify(
                profile.stripe_subscription_id,
                cancel_at_period_end=True  # Schedule the subscription to cancel at the period end
            )
            send_cancel_email(request.user)
            messages.success(request, "Your subscription is scheduled to be cancelled at the end of the billing period. You can continue to use your image genearations until then.")
        except Exception as e:
            messages.error(request, f"An error occurred while trying to cancel your subscription: {str(e)}")
    else:
        messages.error(request, "No active subscription found.")

    return redirect('my_profile')


@login_required
def create_checkout_session(request):
    user_profile = request.user.profile

    try:
        # Check if the user already has a Stripe customer ID
        if user_profile.stripe_customer_id:
            customer_id = user_profile.stripe_customer_id
        else:
            # Create a new Stripe customer and save the ID
            customer = stripe.Customer.create(email=request.user.email)
            customer_id = customer.id
            user_profile.stripe_customer_id = customer_id
            user_profile.save()

        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_1P04fHHfWVyyw5M2VaunOIKS',  # Replace with your Stripe Price ID
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri('/success/'),  # URL to redirect to on successful payment
            cancel_url=request.build_absolute_uri('/cancel/'),    # URL to redirect to on payment cancellation
        )
        return JsonResponse({'sessionId': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)})


def create_stripe_customer(user):
    stripe.api_key = stripe.api_key
    customer = stripe.Customer.create(email=user.email, description=user.id, name=user.username)

    user.profile.stripe_customer_id = customer.id
    user.profile.save()


def payment_cancelled(request):
    # You can add any context or processing you need here
    return render(request, 'registration/payment_cancelled.html')


def payment_success(request):
    # You can add additional context or processing if needed
    #user_profile = request.user.profile
    #user_profile.has_subscription = True
    #user_profile.save()

    return render(request, 'registration/sucess.html')


@csrf_exempt
@require_POST  # This ensures the view only accepts POST requests
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponseForbidden()

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Assuming you have a way to get your user from session information
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')
        # Now, find the user profile with this customer ID
        try:
            user_profile = Profile.objects.get(stripe_customer_id=customer_id)
            # Now you can update the user_profile or perform other actions
            user_profile.image_generations_this_month = 0
            user_profile.save()
            subscription_created.send(sender=Profile, user_profile=user_profile, subscription_id=subscription_id)
            send_subscribe_email(request.user)

        except Profile.DoesNotExist:
            # Handle the case where no matching profile is found
            pass

    if event['type'] == 'invoice.payment_succeeded':
        # Extract customer ID from event
        customer_id = event['data']['object']['customer']

        # Find the user profile associated with this Stripe customer ID
        try:
            user_profile = Profile.objects.get(stripe_customer_id=customer_id)
            user_profile.image_generations_this_month = 0
            user_profile.save()
        except Profile.DoesNotExist:
            # Handle error: Profile not found
            pass

    # Handle the subscription deleted event
    if event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription['customer']

        # Fetch the corresponding user profile using the Stripe customer ID
        try:
            user_profile = Profile.objects.get(stripe_customer_id=customer_id)
            user_profile.has_subscription = False
            user_profile.save()

            # Optionally, log this event or notify the user
        except Profile.DoesNotExist:
            # Handle the case where no profile matches the Stripe customer ID
            pass

    return HttpResponse(status=200)


def update_email(request):
    if request.method == 'POST':
        form = EmailUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            send_profile_email(request.user)
            messages.success(request, 'Your email has been updated.')
            return redirect('my_profile')  # Redirect to the profile page or wherever appropriate
    else:
        form = EmailUpdateForm(instance=request.user)

    return render(request, 'registration/update_email.html', {'form': form})


def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            send_profile_email(request.user)
            update_session_auth_hash(request, form.user)  # Important for keeping the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('my_profile')  # Redirect to a success page or profile
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'registration/change_password.html', {'form': form})