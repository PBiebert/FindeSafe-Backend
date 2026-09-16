from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """User-Model, das die E-Mail statt des Usernamens als Login-Feld nutzt."""

    email = models.EmailField(unique=True)
    agb_accepted = models.BooleanField(verbose_name="AGB akzeptiert", default=False)
    agb_accepted_at = models.DateTimeField(
        verbose_name="AGB akzeptiert am", null=True, blank=True
    )
    privacy_accepted = models.BooleanField(
        verbose_name="Datenschutzerklärung akzeptiert", default=False
    )
    privacy_accepted_at = models.DateTimeField(
        verbose_name="Datenschutzerklärung akzeptiert am", null=True, blank=True
    )

    USERNAME_FIELD = "email"
    # zusätzlich zu USERNAME_FIELD + Passwort bei createsuperuser abgefragte Felder
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
