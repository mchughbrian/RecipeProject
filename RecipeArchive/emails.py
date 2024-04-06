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


def send_subscribe_email(user):
    subject = 'Thank you for Subscribing to RecipeVault!'
    message = """
    Hi {name},

    Thank you for signing up for the RecipeVault Subscription!

    Each month you will get up to 20 image generations with your subscription. 
    
    The images you generate will remain with your account even after you cancel. 
    
    Best,
    The Team
    """.format(name=user)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_cancel_email(user):
    subject = 'Cancellation Confirmation'
    message = """
    Hi {name},

    We are sorry to see you go but want to thank you for subscribing to our service. 
        
    Feel free to continue to use our free tier option!  
        
    If you have any feedback on the subscription service please let us know at support@recipevault.io

    Best,
    The Team
    """.format(name=user)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_profile_email(user):
    subject = 'RecipeVault Profile Update'
    message = """
    Hi {name},

    This email is to inform you that your profile information has been updated.  

    Best,
    The Team
    """.format(name=user)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_invoice_email(user):
    subject = 'Thank you for your payment!'
    message = """
    Hi {name},

    Thank you for your payment for your RecipeVault subscription. 
    
    We value your continued business. 
    
    Please let us know if there is anything we can do better at support@recipevault.io

    Best,
    The Team
    """.format(name=user)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
