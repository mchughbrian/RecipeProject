from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from RecipeArchive.models import Recipe

class Command(BaseCommand):
    help = 'Creates special recipes like "Takeout" and "N/A"'

    def handle(self, *args, **options):
        # Fetch default user
        default_user, created = User.objects.get_or_create(username='default_user')
        if created:
            # Set other default fields for the user if needed, like email, password etc.
            default_user.email = 'default@example.com'
            default_user.set_password('defaultpassword') # You can set this to something secure
            default_user.save()
            self.stdout.write(self.style.SUCCESS('Successfully created default user'))

        # Check if special recipes already exist, if not, create them
        takeout_recipe, created_takeout = Recipe.objects.get_or_create(name="Takeout", user=default_user)
        na_recipe, created_na = Recipe.objects.get_or_create(name="N/A", user=default_user)

        if created_takeout:
            self.stdout.write(self.style.SUCCESS('Successfully created Takeout recipe'))
        else:
            self.stdout.write(self.style.SUCCESS('Takeout recipe already exists'))

        if created_na:
            self.stdout.write(self.style.SUCCESS('Successfully created N/A recipe'))
        else:
            self.stdout.write(self.style.SUCCESS('N/A recipe already exists'))
