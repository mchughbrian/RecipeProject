from django.core.mail import send_mail
from django.conf import settings


def send_welcome_email(user):
    subject = 'Welcome to RecipeVault!'
    message = """
    Hi {name},
        
    Thank you for signing up for the RecipeVault!
        
    Our goal is to create an easy way for you to save your recipes and bring them to life with images. 
        
    Check out our Image Generation Feature to bring your RecipeVault to life. 
        
    We are a new application, please feel free to give us feedback at support@recipevault.io
        
    Best,
    The Team
    """.format(name=user)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

