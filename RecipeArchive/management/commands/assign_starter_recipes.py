import json

import requests
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from pathlib import Path
from RecipeArchive.models import Recipe  # Adjust the import path based on your project
import os


def assign_starter_recipes(user):
    json_url = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/recipes/starter/starter_recipes.json'  # Update the path
    response = requests.get(json_url)
    if response.status_code == 200:
        recipes = response.json()  # Parse the JSON directly from the response
        for recipe_data in recipes:
            recipe = Recipe(
                user=user,
                name=recipe_data['name'],
                ingredients=recipe_data['ingredients'],
                instructions=recipe_data['instructions'],
                meal_type=recipe_data['meal_type'],
                rating=recipe_data['rating']
            )
            # Handle the image
            image_rel_path = recipe_data.get('image_path')
            if image_rel_path:
                media_root = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/'
                image_abs_url = f'{media_root}{image_rel_path}'
                # Fetch the image content from S3 using requests (assuming public access or presigned URL)
                try:
                    response = requests.get(image_abs_url)
                    if response.status_code == 200:
                        # Create a ContentFile object from the downloaded image content
                        image_content = ContentFile(response.content)
                        # Use the last part of the image_rel_path as the name for saving
                        image_name = image_rel_path.split('/')[-1]  # Extract the filename from the path
                        # Save the image to the model's ImageField
                        recipe.image.save(image_name, image_content, save=True)
                    else:
                        print(f"Could not retrieve image from {image_abs_url}. Status code: {response.status_code}")
                except Exception as e:
                    print(f"Error fetching or saving image from {image_abs_url}: {e}")

            recipe.save()
