from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import EmailVerificationCode
from accounts.services import generate_verification_code

User = get_user_model()


class ResendVerificationCodeTest(APITestCase):
    def setUp(self):
        """Legt einen inaktiven Benutzer an und leert den Throttle-Cache."""

        # Der Throttle speichert seine Zähler im Cache – ohne Leeren würden
        # sich die Tests gegenseitig beeinflussen.
        cache.clear()
        self.addCleanup(cache.clear)

        self.url = reverse("resend-verification-code")
        self.email = "max.mustermann@test.de"
        self.user = User.objects.create_user(
            username=self.email,
            email=self.email,
            password="TestCase123!",
            first_name="Max",
            last_name="Mustermann",
            is_active=False,
        )

    @patch("accounts.api.views.enqueue_activation_email")
    def test_post_resend_valid_email_return_200_and_enqueues_email(self, mock_enqueue):
        """Testet, dass ein neuer Code erstellt und die Mail eingereiht wird."""

        response = self.client.post(self.url, {"email": self.email}, format="json")
        code = EmailVerificationCode.objects.get(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(code.code), 6)
        mock_enqueue.assert_called_once_with(self.user.id, code.code)

    @patch("accounts.api.views.enqueue_activation_email")
    def test_post_resend_replaces_old_code(self, mock_enqueue):
        """Testet, dass alte Codes gelöscht werden und nur der neue übrig bleibt."""

        old_code = generate_verification_code(self.user)
        old_code.attempts = 2
        old_code.save(update_fields=["attempts"])

        response = self.client.post(self.url, {"email": self.email}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # get() schlägt fehl, wenn es keinen oder mehrere Codes gibt
        new_code = EmailVerificationCode.objects.get(user=self.user)
        self.assertNotEqual(new_code.pk, old_code.pk)
        self.assertEqual(new_code.attempts, 0)

    @patch("accounts.api.views.enqueue_activation_email")
    def test_post_resend_unknown_email_return_400(self, mock_enqueue):
        """Testet, dass eine unbekannte E-Mail abgelehnt wird und keine Mail entsteht."""

        response = self.client.post(
            self.url, {"email": "unbekannt@test.de"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(EmailVerificationCode.objects.exists())
        mock_enqueue.assert_not_called()

    @patch("accounts.api.views.enqueue_activation_email")
    def test_post_resend_active_user_return_400(self, mock_enqueue):
        """Testet, dass für bereits aktivierte Benutzer kein Code gesendet wird."""

        self.user.is_active = True
        self.user.save(update_fields=["is_active"])

        response = self.client.post(self.url, {"email": self.email}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(EmailVerificationCode.objects.exists())
        mock_enqueue.assert_not_called()

    def test_post_resend_unknown_and_active_return_same_error(self):
        """Testet, dass beide Fehlerfälle dieselbe Meldung liefern (keine Enumeration)."""

        unknown = self.client.post(
            self.url, {"email": "unbekannt@test.de"}, format="json"
        )
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])
        active = self.client.post(self.url, {"email": self.email}, format="json")
        self.assertEqual(unknown.data, active.data)

    def test_post_resend_missing_email_return_400(self):
        """Testet, dass eine fehlende E-Mail mit 400 abgelehnt wird."""

        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_post_resend_invalid_email_format_return_400(self):
        """Testet, dass eine syntaktisch ungültige E-Mail mit 400 abgelehnt wird."""

        response = self.client.post(self.url, {"email": "keine-mail"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("accounts.api.views.enqueue_activation_email")
    def test_post_resend_throttled_after_limit_return_429(self, mock_enqueue):
        """Testet, dass nach 3 Anfragen pro Stunde die vierte mit 429 geblockt wird."""

        for _ in range(3):
            response = self.client.post(self.url, {"email": self.email}, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(self.url, {"email": self.email}, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(mock_enqueue.call_count, 3)
