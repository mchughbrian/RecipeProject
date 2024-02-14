import json
from django.conf import settings
from django.core.files import File
from django.core.files.images import ImageFile
from pathlib import Path
from RecipeArchive.models import Recipe  # Adjust the import path based on your project
import os


def assign_starter_recipes(user):
    path = Path(settings.BASE_DIR) / 'data/starter_recipes.json'  # Update the path
    with open(path, 'r') as file:
        recipes = json.load(file)
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
                media_root = Path(settings.MEDIA_ROOT)
                image_rel_path = Path(image_rel_path)  # Assuming image_rel_path is a string
                image_abs_path = media_root / image_rel_path
                if image_abs_path.exists():
                    # Open the image file in binary mode
                    with image_abs_path.open('rb') as img_file:
                        # Django's ImageField requires a File or ImageFile object
                        try:
                            recipe.image.save(image_rel_path.name, File(img_file), save=True)
                        except Exception as e:
                            print(f"Error saving image: {e}")
                recipe.save()