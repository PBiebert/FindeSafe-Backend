from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """User-Model, das die E-Mail statt des Usernamens als Login-Feld nutzt."""

    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    # zusätzlich zu USERNAME_FIELD + Passwort bei createsuperuser abgefragte Felder
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
