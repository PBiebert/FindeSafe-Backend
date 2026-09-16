from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterTest(APITestCase):
    def setUp(self):
        """Setzt die Testumgebung auf und initialisiert die Testdaten."""

        self.register_url = reverse("register")
        self.user_data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": "max.mustermann@test.de",
            "password": "TestCase123!",
            "confirm_password": "TestCase123!",
            "agb_accepted": True,
            "privacy_accepted": True,
        }

    def test_post_register_valid_data_return_201(self):
        """Testet die Registrierung mit gültigen Daten und erwartet einen 201-Statuscode."""

        response = self.client.post(self.register_url, self.user_data, format="json")
        user = User.objects.get(email=self.user_data["email"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(user.is_active)

    def test_post_register_password_mismatch_return_400(self):
        """Testet die Registrierung mit nicht übereinstimmenden Passwörtern und erwartet einen 400-Statuscode."""

        self.user_data["confirm_password"] = "Mismatch123!"
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_register_email_already_exists_return_400(self):
        """Testet die Registrierung mit einer bereits existierenden E-Mail-Adresse und erwartet einen 400-Statuscode."""

        user_data = {
            "username": "max.mustermann@test.de",
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": "max.mustermann@test.de",
            "password": "TestCase123!",
            "agb_accepted": True,
            "privacy_accepted": True,
        }

        User.objects.create_user(**user_data)

        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_register_agb_not_accepted_return_400(self):
        """Testet die Registrierung ohne Akzeptanz der AGB und erwartet einen 400-Statuscode."""

        self.user_data["agb_accepted"] = False
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_register_privacy_not_accepted_return_400(self):
        """Testet die Registrierung ohne Akzeptanz der Datenschutzerklärung und erwartet einen 400-Statuscode."""

        self.user_data["privacy_accepted"] = False
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_register_missing_email_return_400(self):
        """Testet die Registrierung ohne E-Mail-Adresse und erwartet einen 400-Statuscode."""

        self.user_data["email"] = ""
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
