# We import necessary modules from Django's test framework and auth models
from django.contrib.auth.models import User
from django.test import TestCase, Client
from unittest.mock import patch
from RecipeArchive.models import Profile
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from .models import Recipe
from io import BytesIO
import os

# We define a new test case by creating a subclass of django.test.TestCase
class HomeViewTest(TestCase):
    # setUp is a special method that is run before each test
    # We use it to set up the state for our tests
    def setUp(self):
        # Client is a class that acts like a dummy web browser
        # We can use it to simulate GET and POST requests
        self.client = Client()

        # We create a test user that we can use for authentication in our tests
        self.test_user = User.objects.create_user(username='testuser', password='testpass')

    # test_home_view is an example of a test method
    # Each test method should start with the word "test"
    def test_home_view(self):
        # We simulate a login with the test user's credentials
        self.client.login(username='testuser', password='testpass')

        # We use the client to make a GET request to the home view
        # and store the response in a variable
        response = self.client.get('/home/')

        # We use an assert method to check that the home view returned a HTTP 200 status code
        # If it didn't, the test will fail
        self.assertEqual(response.status_code, 200)


#This test is testing payments and that payments updates the profile
class PaymentTests(TestCase):

    def setUp(self):
        # Set up data for the tests
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.profile, created = Profile.objects.get_or_create(user=self.user)

    @patch('stripe.checkout.Session.create')
    def test_successful_payment(self, mock_checkout_session_create):
        # Mock the Stripe Checkout Session creation
        mock_checkout_session_create.return_value = {'id': 'cs_test'}

        self.client.login(username='testuser', password='password')
        response = self.client.post('/create-checkout-session/', {'plan_id': 'basic_plan'})

        self.client.get('/success/')  # Assuming this URL triggers payment_success

        # Check if the profile was updated
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.has_subscription)


# Mock classes
class MockResponse:
    def __init__(self):
        self.data = [{'url': 'https://via.placeholder.com/1024'}]


class ImageGenerationTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.profile, created = Profile.objects.get_or_create(user=self.user)
        self.profile.generated_images_count = 5  # Set the count to the limit
        self.profile.has_subscription = False  # Ensure the user is a non-subscriber
        self.profile.save()

    def test_image_generation_limit_non_subscriber(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post('/generate-image/', {'prompt': 'test prompt'})
        self.assertEqual(response.status_code, 403)
        self.assertIn('Free image generation limit reached', response.json()['error'])

    def test_image_generation_limit_subscriber(self):
        self.profile.has_subscription = True
        self.profile.image_generations_this_month = 20
        self.profile.save()

        self.client.login(username='testuser', password='password')
        response = self.client.post('/generate-image/', {'prompt': 'test prompt'})
        self.assertEqual(response.status_code, 403)
        self.assertIn('Monthly image generation limit reached', response.json()['error'])

    #@patch('openai.images.generate')
    #def test_successful_image_generation(self, mock_openai):
     #   mock_openai.return_value = MockResponse()
      #  self.profile.generated_images_count = 0  # Set the count to the limit
       # self.profile.has_subscription = True  # Ensure the user is a non-subscriber
        #self.profile.save()
        #self.client.login(username='testuser', password='password')
        #TODO fix this test case
        #response = self.client.post('/generate-image/', {'prompt': 'test prompt'})
        #print(response.content)
        #self.assertEqual(response.status_code, 200)
        #self.assertIn('https://via.placeholder.com/1024', response.json()['image_url'])


@override_settings(MEDIA_ROOT='/tmp/django_test')
class RecipeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user1 = User.objects.create_user(username='testuser1', password='password123')
        self.user2 = User.objects.create_user(username='testuser2', password='password123')
        self.client.login(username='testuser', password='testpassword')

    @patch('requests.get')
    def test_add_recipe_with_image_url(self, mock_get):
        # Mock the response from requests.get to simulate fetching an image
        recipe_count = Recipe.objects.count()
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = BytesIO(b'test image content').getvalue()

        response = self.client.post(reverse('add_recipe'), {
            'title': 'Test Recipe',  # Assuming 'title' is correct based on your initial test
            'name': 'Test Recipe Name',
            'ingredients': 'Test Ingredients',
            'meal_type': 'Breakfast',  # Assuming 'meal_type' expects a string like 'Breakfast', 'Lunch', etc.
            'rating': '5',  # Assuming 'rating' is a numeric field represented as a string in POST data
            'image_url': 'https://via.placeholder.com/1024',
            # Add other required fields here
        })

        # Check for form errors if the response is not a redirect
        if response.status_code != 302:
            print(response.context['form'].errors)

        self.assertEqual(response.status_code, 302)  # Assuming redirect to 'home'
        self.assertEqual(Recipe.objects.count(), recipe_count+1)
        recipe = Recipe.objects.last()
        self.assertTrue(recipe.image)  # Check if the image field is populated
        self.assertIn('ImageGen_', recipe.image.name)  # Check filename pattern

        # Cleanup the created file
        recipe.image.delete(save=False)

    def test_image_upload(self):
        # Path to a test image file
        test_image_path = os.path.join(os.path.dirname(__file__), 'test_data', 'test_image.png')
        with open(test_image_path, 'rb') as img:
            response = self.client.post(reverse('add_recipe'), {
                'title': 'Test Recipe2',  # Assuming 'title' is correct based on your initial test
                'name': 'Test Recipe Name2',
                'ingredients': 'Test Ingredients2',
                'meal_type': 'Breakfast',  # Assuming 'meal_type' expects a string like 'Breakfast', 'Lunch', etc.
                'rating': '5',
                'image': SimpleUploadedFile(img.name, img.read(), content_type='image/png'),
                # Include other required form fields
                })

        self.assertEqual(response.status_code, 302)  # Assuming successful upload redirects
        self.assertTrue(Recipe.objects.exists())  # Ensure the recipe was created
        recipe = Recipe.objects.last()
        self.assertTrue(recipe.image)  # Ensure an image is associated with the recipe
        # Clean up
        recipe.image.delete(save=True)

    def test_unique_file_storage2(self):
        # Path to a test image file
        self.client.login(username='testuser1', password='password123')
        recipe_count = Recipe.objects.count()
        test_image_path = os.path.join(os.path.dirname(__file__), 'test_data', 'test_image.png')
        with open(test_image_path, 'rb') as img:
            response = self.client.post(reverse('add_recipe'), {
                'title': 'Test Recipe2',  # Assuming 'title' is correct based on your initial test
                'name': 'Test Recipe Name2',
                'ingredients': 'Test Ingredients2',
                'meal_type': 'Breakfast',  # Assuming 'meal_type' expects a string like 'Breakfast', 'Lunch', etc.
                'rating': '5',
                'image': SimpleUploadedFile(img.name, img.read(), content_type='image/png'),
                # Include other required form fields
            })

        self.assertEqual(response.status_code, 302)  # Assuming successful upload redirects
        self.assertEqual(Recipe.objects.count(), recipe_count+1)
        recipe = Recipe.objects.last()
        self.assertTrue(recipe.image)  # Ensure an image is associated with the recipe
        self.client.logout()

        # Log in as the second user
        self.client.login(username='testuser2', password='password123')


        with open(test_image_path, 'rb') as img:
            response = self.client.post(reverse('add_recipe'), {
                'title': 'Test Recipe2',  # Assuming 'title' is correct based on your initial test
                'name': 'Test Recipe Name2',
                'ingredients': 'Test Ingredients2',
                'meal_type': 'Breakfast',  # Assuming 'meal_type' expects a string like 'Breakfast', 'Lunch', etc.
                'rating': '5',
                'image': SimpleUploadedFile(img.name, img.read(), content_type='image/png'),
                # Include other required form fields
            })

        if response.status_code != 302:  # Assuming a successful submission redirects
            print(response.content)  # Or `print(response.context['form'].errors)` for form errors

        # Retrieve the uploaded images for both users
        recipe1 = Recipe.objects.filter(user=self.user1).latest('id')
        recipe2 = Recipe.objects.filter(user=self.user2).latest('id')

        Recipe.objects.last()
        # Verify that the paths of the uploaded files are different
        self.assertNotEqual(recipe1.image.name, recipe2.image.name)

        # Clean up: Delete the images to clean up the file system
        recipe1.image.delete(save=False)
        recipe2.image.delete(save=False)