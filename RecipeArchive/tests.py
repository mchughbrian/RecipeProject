# We import necessary modules from Django's test framework and auth models
from django.test import Client, TestCase
from django.contrib.auth.models import User

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
