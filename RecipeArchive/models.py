# Create your models here.
# This is a command-line utility that lets you interact with your project.

# Django's built-in models and User model are imported
from django.db import models
from django.contrib.auth.models import User

# Recipe model is defined
class Recipe(models.Model):
    # name of the recipe as a string of maximum length 200 characters
    name = models.CharField(max_length=200)

    # description of the recipe as a text field
    #description = models.TextField()

    ingredients = models.TextField()

    # image of the recipe, uploaded to the "recipes/" directory
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)  # this makes the field optional

    # cuisine of the recipe as a string of maximum length 100 characters
    #cuisine = models.CharField(max_length=100)

    MEAL_TYPE_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
        ('Dessert', 'Dessert'),
        ('Snack', 'Snack'),
        ('Drink', 'Drink'),
        ('Other', 'Other'),
    ]

    # other fields...

    meal_type = models.CharField(max_length=100, choices=MEAL_TYPE_CHOICES, default='Other')

    # protein type of the recipe as a string of maximum length 100 characters
    protein_type = models.CharField(max_length=100)

    RATING_CHOICES = [(i, i) for i in range(1, 6)]  # This creates a list of tuples for choices

    # rating of the recipe as an integer
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)

    # date when the recipe was added, automatically set to the current date and time
    date_added = models.DateTimeField(auto_now_add=True)

    # the user who added the recipe, linked via a foreign key to the User model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
