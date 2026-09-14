from django.contrib.auth.models import AbstractUser


# staff accounts for the Django admin; visitors are identified per comment, not by an account
class User(AbstractUser):
    pass
