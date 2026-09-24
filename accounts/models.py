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


class EmailVerificationCode(models.Model):
    """Model für die Speicherung von E-Mail-Verifizierungscodes."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "E-Mail-Verifizierungscode"
        verbose_name_plural = "E-Mail-Verifizierungscodes"

    def __str__(self):
        return f"{self.user.email} - Bestätigungscode"
