from rest_framework import status
from rest_framework.authtoken.views import Response
from rest_framework.views import APIView

from accounts.api.serializers import RegisterSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Registrierung erfolgreich"}, status=status.HTTP_201_CREATED
        )
