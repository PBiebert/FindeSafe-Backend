from rest_framework import status
from rest_framework.authtoken.views import Response
from rest_framework.views import APIView


class RegisterView(APIView):
    def post(self, request):

        return Response(
            {"message": "Registration successful."}, status=status.HTTP_201_CREATED
        )
