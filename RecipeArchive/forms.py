from django import forms
from .models import Recipe


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ['name', 'description', 'image', 'meal_type', 'cuisine', 'protein_type', 'rating']
