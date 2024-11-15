# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import CustomUser
from .serializers import CustomUserSerializer

#json
class CustomUserDetailView(APIView):
    def get(self, request, email):
        try:
            user = CustomUser.objects.get(email=email)
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
