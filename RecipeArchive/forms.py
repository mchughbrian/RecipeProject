from django import forms
from django.core.exceptions import ValidationError

from .models import Recipe
from .models import MealPlan
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    cookbook_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)  #custom required field

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'cookbook_name']

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        if commit:
            user.save()
            user.profile.cookbook_name = self.cleaned_data['cookbook_name']
            user.profile.save()
        return user


    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        password_help_text = """
            Your password must contain at least:
            - 8 characters
            - 1 number
            - 1 uppercase letter
            - 1 lowercase letter
            """
        self.fields['password1'].help_text = password_help_text.strip()


    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username is already associated with an account.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email is already associated with an account.")
        return email

class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ['name', 'ingredients', 'image', 'meal_type', 'rating']


class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['name', 'days', 'breakfast', 'lunch', 'dinner']
        widgets = {
            'breakfast': forms.CheckboxInput,
            'lunch': forms.CheckboxInput,
            'dinner': forms.CheckboxInput,
        }



class MealDayForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # get the user from the keyword arguments
        days = kwargs.pop('days')  # get the number of days
        meals = kwargs.pop('meals')  # get the selected meals
        self.name = kwargs.pop('name', None)  # get the name, if provided
        super().__init__(*args, **kwargs)  # call the parent's __init__

        from .views import get_available_recipes_for_user
        available_recipes = get_available_recipes_for_user(self.user)

        # for each day, we create fields for each meal
        for i in range(1, days + 1):
            if meals.get('breakfast'):  # if breakfast is True
                self.fields['breakfast_%s' % i] = forms.ModelChoiceField(queryset=available_recipes, required=False)
            if meals.get('lunch'):  # if lunch is True
                self.fields['lunch_%s' % i] = forms.ModelChoiceField(queryset=available_recipes, required=False)
            if meals.get('dinner'):  # if dinner is True
                self.fields['dinner_%s' % i] = forms.ModelChoiceField(queryset=available_recipes, required=False)


class RecipeSearchForm(forms.Form):
    query = forms.CharField(label="Search for a recipe", max_length=255)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['cookbook_name']
        # Add other profile fields as needed


class CustomUserChangeForm(UserChangeForm):
    password = None  # Exclude password field

    class Meta:
        model = Profile
        fields = ['cookbook_name']  # Specify the fields to include
        # If you want to include the password change, use PasswordChangeForm separately

