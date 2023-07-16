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
        fields = ['days', 'breakfast', 'lunch', 'dinner']
        widgets = {
            'breakfast': forms.CheckboxInput,
            'lunch': forms.CheckboxInput,
            'dinner': forms.CheckboxInput,
        }


class MealDayForm(forms.Form):
    # we'll overwrite the __init__ method to accept additional arguments
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # get the user from the keyword arguments
        days = kwargs.pop('days')  # get the number of days
        meals = kwargs.pop('meals')  # get the selected meals
        super().__init__(*args, **kwargs)  # call the parent's __init__

        # for each day, we create fields for each meal
        #for i in range(days):
        #    for meal in meals:
                # we create a new ModelChoiceField for the meal of the day
        #        self.fields['day_%s_meal_%s' % (i, meal)] = forms.ModelChoiceField(
        #            queryset=Recipe.objects.filter(user=self.user),  # we only want to show the user's recipes
        #            label='Day %s: %s' % (i + 1, meal)  # the label will show which day and meal this field is for
        #        )
# for each day, we create fields for each meal
        for i in range(1, days + 1):
            if meals.get('breakfast'):  # if breakfast is True
                self.fields['breakfast_%s' % i] = forms.ModelChoiceField(queryset=Recipe.objects.all(), required=False)
            if meals.get('lunch'):  # if lunch is True
                self.fields['lunch_%s' % i] = forms.ModelChoiceField(queryset=Recipe.objects.all(), required=False)
            if meals.get('dinner'):  # if dinner is True
                self.fields['dinner_%s' % i] = forms.ModelChoiceField(queryset=Recipe.objects.all(), required=False)