from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.serializers import (
    EmailVerificationSerializer,
    RegisterSerializer,
    ResendVerificationCodeSerializer,
)
from accounts.api.services import enqueue_activation_email
from accounts.models import EmailVerificationCode
from accounts.services import generate_verification_code

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        verification_code = generate_verification_code(user)
        enqueue_activation_email(user.id, verification_code.code)

        return Response(
            {"message": "Registrierung erfolgreich"}, status=status.HTTP_201_CREATED
        )


class AccountActivateView(APIView):
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Aktivierung erfolgreich"}, status=status.HTTP_200_OK
        )


class ResendVerificationCodeView(APIView):
    def post(self, request):
        serializer = ResendVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        EmailVerificationCode.objects.filter(user=user).delete()

        verification_code = generate_verification_code(user)
        enqueue_activation_email(user.id, verification_code.code)

        return Response({"message": "Code wurde gesendet"})
