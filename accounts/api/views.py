from rest_framework import status
from rest_framework.authtoken.views import Response
from rest_framework.views import APIView

from accounts.api.serializers import RegisterSerializer
from accounts.services import generate_verification_code


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        print(user)
        generate_verification_code(user)

        return Response(
            {"message": "Registrierung erfolgreich"}, status=status.HTTP_201_CREATED
        )
