from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import EmailVerificationCode

User = get_user_model()


class AccountVerificationTest(APITestCase):
    def setUp(self):
        """Legt einen inaktiven Benutzer mit gültigem Code für die Tests an."""

        self.url = reverse("account-verification")
        self.email = "max.mustermann@test.de"
        self.user = User.objects.create_user(
            username=self.email,
            email=self.email,
            password="TestCase123!",
            is_active=False,
        )
        self.code = EmailVerificationCode.objects.create(
            user=self.user,
            code="123456",
            expires_at=timezone.now() + timedelta(minutes=5),
        )

    def _post(self, **overrides):
        """Sendet die Aktivierungsanfrage; einzelne Felder sind überschreibbar."""

        data = {"email": self.email, "code": "123456"}
        data.update(overrides)
        return self.client.post(self.url, data, format="json")

    def test_post_verification_valid_code_return_200(self):
        """Testet die Aktivierung mit gültigem Code: Benutzer aktiv, Code gelöscht."""

        response = self._post()
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_active)
        self.assertFalse(EmailVerificationCode.objects.filter(user=self.user).exists())

    def test_post_verification_wrong_code_return_400(self):
        """Testet einen falschen Code: 400, Fehlversuch gezählt, Benutzer bleibt inaktiv."""

        response = self._post(code="000000")
        self.user.refresh_from_db()
        self.code.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.is_active)
        self.assertEqual(self.code.attempts, 1)

    def test_post_verification_too_many_attempts_deletes_code(self):
        """Testet, dass der Code nach zu vielen Fehlversuchen gelöscht wird.

        Aktuelles Verhalten: Der Code wird beim 4. Fehlversuch gelöscht
        (Prüfung ``attempts > 3``).
        """

        for _ in range(4):
            response = self._post(code="000000")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(EmailVerificationCode.objects.filter(user=self.user).exists())

        # Auch der richtige Code funktioniert danach nicht mehr
        response = self._post()
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.is_active)

    def test_post_verification_expired_code_return_400(self):
        """Testet einen abgelaufenen Code: 400 und der Code wird gelöscht."""

        self.code.expires_at = timezone.now() - timedelta(minutes=1)
        self.code.save(update_fields=["expires_at"])

        response = self._post()
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.is_active)
        self.assertFalse(EmailVerificationCode.objects.filter(user=self.user).exists())

    def test_post_verification_unknown_email_return_400(self):
        """Testet eine unbekannte E-Mail-Adresse und erwartet einen 400-Statuscode."""

        response = self._post(email="unbekannt@test.de")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_verification_no_code_exists_return_400(self):
        """Testet einen Benutzer ohne Code und erwartet einen 400-Statuscode."""

        self.code.delete()
        response = self._post()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_verification_uses_newest_code_only(self):
        """Testet, dass nur der neueste Code gilt und ältere abgelehnt werden."""

        EmailVerificationCode.objects.create(
            user=self.user,
            code="654321",
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        response = self._post(code="123456")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.is_active)

        response = self._post(code="654321")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_active)

    def test_post_verification_missing_fields_return_400(self):
        """Testet fehlende Pflichtfelder (E-Mail bzw. Code) und erwartet 400."""

        response = self.client.post(self.url, {"email": self.email}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.url, {"code": "123456"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
