import secrets

from django.utils import timezone

from .models import EmailVerificationCode


def generate_verification_code(user):
    """
    Erstellt einen neuen E-Mail-Verifizierungscode für den angegebenen Benutzer.

    Args:
        user (CustomUser): Der Benutzer, für den der Verifizierungscode erstellt werden soll.
    """

    code = str(secrets.randbelow(900000) + 100000)

    verification_code = EmailVerificationCode.objects.create(
        user=user,
        code=code,
        expires_at=timezone.now() + timezone.timedelta(minutes=5),
    )

    return verification_code
