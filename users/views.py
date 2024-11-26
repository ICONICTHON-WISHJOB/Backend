from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import SignupSerializer, LoginRequestSerializer
from .models import CustomUser, Company
from drf_yasg.utils import swagger_auto_schema

class SignupView(APIView):
    @swagger_auto_schema(request_body=SignupSerializer)
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginRequestSerializer)
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            password = serializer.validated_data['password']

            is_company_user = user_id.endswith('@company.com')

            try:
                if is_company_user:
                    user = Company.objects.get(company_id=user_id)
                else:
                    user = CustomUser.objects.get(email=user_id)

                if user.check_password(password):
                    request.session['email'] = user_id
                    request.session['user_type'] = 1 if is_company_user else 0

                    return Response({
                        "message": "Login successful",
                        "id": user_id,
                        "user_type": 1 if is_company_user else 0
                    }, status=status.HTTP_200_OK)

            except (Company.DoesNotExist, CustomUser.DoesNotExist):
                pass
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
