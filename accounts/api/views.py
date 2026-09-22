from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.views import Response
from rest_framework.views import APIView

from accounts.api.serializers import EmailVerificationSerializer, RegisterSerializer
from accounts.services import generate_verification_code

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        generate_verification_code(user)

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
    pass
