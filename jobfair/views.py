from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import CustomUser, Company, Booth, BoothQueue
from users.serializers import BoothSerializer
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404

class ReserveBoothView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booth_id):
        user = request.user
        try:
            booth = Booth.objects.get(id=booth_id)
        except Booth.DoesNotExist:
            return Response({"error": "Booth not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is already in the queue
        if BoothQueue.objects.filter(booth=booth, user=user).exists():
            return Response({"message": "Already in the queue"}, status=status.HTTP_400_BAD_REQUEST)

        # Add user to the queue
        position = BoothQueue.objects.filter(booth=booth).count() + 1
        BoothQueue.objects.create(booth=booth, user=user, position=position)

        return Response({"message": f"Added to queue at position {position}"}, status=status.HTTP_201_CREATED)

class CheckQueuePositionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, booth_id):
        user = request.user
        try:
            queue_entry = BoothQueue.objects.get(booth_id=booth_id, user=user)
            position = queue_entry.position
            return Response({"position": position}, status=status.HTTP_200_OK)
        except BoothQueue.DoesNotExist:
            return Response({"error": "You are not in the queue for this booth"}, status=status.HTTP_404_NOT_FOUND)


class BoothListView(APIView):
    def get(self, request, day, floor):
        booths = Booth.objects.filter(day=day, floor=floor)
        serializer = BoothSerializer(booths, many=True)
        return Response({"booths": serializer.data}, status=status.HTTP_200_OK)


class BoothApplyView(APIView):
    #permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                          description='ID of the user making the reservation'),
                'booth_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the booth'),
            },
            required=['user_id', 'booth_id'],
        ),
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'boothName': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the booth'),
                'waitTime': openapi.Schema(type=openapi.TYPE_INTEGER, description='Calculated wait time in minutes'),
            }
        )}
    )

    def post(self, request):
        user_id = request.data.get('user_id')  # unique ID for the user
        booth_id = request.data.get('booth_id')

        # Fetch the user by ID
        user = get_object_or_404(CustomUser, id=user_id)
        # Fetch the booth by ID
        booth = get_object_or_404(Booth, booth_id=booth_id)

        booth.queue.add(user)
        booth.wait_time = booth.calculate_wait_time()
        booth.save()

        new_reservation = {
            "boothid": booth.booth_id,
            "boothName": booth.boothName,
            "doneType": 0,  # 0: 예정
            "position_in_queue": booth.queue.count()  # 현재 대기 순서
        }

        if user.reservation_status is None:
            user.reservation_status = []

        user.reservation_status.append(new_reservation)
        user.save()

        return Response({
            "boothName": booth.boothName,
            "waitTime": booth.wait_time
        }, status=status.HTTP_200_OK)

class BoothPossibleNowView(APIView):
    def get(self, request):
        # Filter booths where wait_time is less than 10
        booths = Booth.objects.filter(wait_time__lt=10)
        for i in booths:
            print(i)

        # Format the response as requested
        booth_data = [
            {
                "boothId": booth.booth_id,
                "boothNum": booth.boothNum,
                "boothCate": booth.boothCate,
                "boothName": booth.boothName
            }
            for booth in booths
        ]

        response_data = {
            "booths": booth_data,
            "totalCnt": booths.count()
        }

        return Response(response_data, status=status.HTTP_200_OK)

import openai
import os
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import CustomUser

openai.api_key=os.getenv('GPT_KEY')
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import CustomUser
import openai

class RecommendView(APIView):
    @swagger_auto_schema(
        operation_description="Recommend a category based on user's self-introduction.",
        responses={
            200: openapi.Response(
                description="Recommended category",
                examples={"application/json": {"recommended_category": "기술연구"}}
            ),
            401: "User not authenticated",
            404: "User not found",
            500: "Failed to connect to OpenAI API"
        }
    )
    def post(self, request):
        email = request.session.get('email')
        if not email:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = CustomUser.objects.get(email=email)
            self_introduction = user.self_introduction
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        prompt = f"Analyze the following self-introduction and determine if it best matches one of these categories: 기술연구, 채용상담관, or 스타트업.\n\nSelf-introduction:\n{self_introduction}\n\nRespond with one of the categories only."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=10,
                temperature=0.5,
            )
            category = response['choices'][0]['message']['content'].strip()
            user.recommend = category
            user.save()
        except Exception as e:
            return Response({"error": "Failed to connect to OpenAI API", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"recommended_category": category}, status=status.HTTP_200_OK)
