# We import necessary modules from Django's test framework and auth models
from django.contrib.auth.models import User
from django.test import TestCase, Client
from unittest.mock import patch
from RecipeArchive.models import Profile


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
class MockData:
    def __init__(self, url):
        self.url = url

class MockResponse:
    def __init__(self):
        self.data = [MockData("https://via.placeholder.com/1024")]


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

    @patch('openai.images.generate')
    def test_successful_image_generation(self, mock_openai):
        mock_openai.return_value = MockResponse()
        #TODO fix this test case
        self.client.login(username='testuser', password='password')
        response = self.client.post('/generate-image/', {'prompt': 'test prompt'})
        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('https://via.placeholder.com/1024', response.json()['image_url'])
