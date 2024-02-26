from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q
from storages.backends.s3boto3 import S3Boto3Storage


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None


class MediaStorage(S3Boto3Storage):
    location = 'media'  # This is the "directory" in your S3 bucket where media files will be stored
    file_overwrite = False  # To avoid overwriting files with the same name