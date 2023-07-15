from django import forms
from .models import Recipe
from .models import MealPlan



class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ['name', 'ingredients', 'image', 'meal_type', 'rating']


class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['num_days', 'breakfast', 'lunch', 'dinner']
