from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField()
    confirm_password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    agb_accepted = serializers.BooleanField(required=True)
    privacy_accepted = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "agb_accepted",
            "privacy_accepted",
        )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bitte prüfen Sie Ihre Eingabe.")
        return value

    def validate_agb_accepted(self, value):
        if not value:
            raise serializers.ValidationError(
                "Sie müssen die AGB akzeptieren, um fortzufahren."
            )
        return value

    def validate_privacy_accepted(self, value):
        if not value:
            raise serializers.ValidationError(
                "Sie müssen die Datenschutzerklärung akzeptieren, um fortzufahren."
            )
        return value

    def validate(self, data):
        """Prüft, dass Passwort und Passwort-Wiederholung übereinstimmen."""

        if data["password"] != data.pop("confirm_password"):
            raise serializers.ValidationError("Die Passwörter stimmen nicht überein.")
        return data

    def create(self, validated_data):
        """Erstellt einen neuen Benutzer mit den validierten Daten."""
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            agb_accepted=validated_data["agb_accepted"],
            privacy_accepted=validated_data["privacy_accepted"],
        )
        return user
