
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from users.models import CustomUser, Booth, InterestCategory
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated


class MyPageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, userId):
        user = get_object_or_404(CustomUser, id=userId)

        interested_companies = [
            {"name": company.name, "promotional_content": company.promotional_content}
            for company in user.interested_companies.all()
        ]

        # 참여했던 부스 가져오기
        # participated_booths = [
        #     {
        #         "booth_id": booth.booth_id,
        #         "company_name": booth.company.name,
        #         "day": booth.day,
        #         "floor": booth.floor,
        #         "boothNum": booth.boothNum,
        #         "boothCate": booth.boothCate,
        #         "boothName": booth.boothName,
        #     }
        #     for booth in user.participated_booths.all()
        # ]

        # 사용자 정보를 JSON 형식으로 반환
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phoneNum": user.phoneNum,
            "birth": user.birth,
            "age": user.age,
            "school": user.school,
            "department": user.department,
            "admission_date": user.admission_date,
            "graduation_date": user.graduation_date,
            "experience": user.experience,
            "self_introduction": user.self_introduction,
            "companies_of_interest": user.companies_of_interest,
            "interested_companies": interested_companies,
            # "participated_booths": participated_booths,
        }
        return JsonResponse(user_data)


class MyPageInterestView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, userId):
        user = get_object_or_404(CustomUser, id=userId)

        interest_categories = user.interest_categories.all()
        interest_category_names = [category.name for category in interest_categories]

        response_data = {
            "interest_categories": interest_category_names
        }
        return JsonResponse(response_data)


class ReservationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, userId, doneType=None):
        user = get_object_or_404(CustomUser, id=userId)

        reservation_status = user.reservation_status or []

        if doneType is not None:
            filtered_reservations = [
                reservation for reservation in reservation_status if reservation.get("doneType") == doneType
            ]
        else:
            filtered_reservations = reservation_status

        response_data = {
            "reservationList": filtered_reservations,
            "totalCnt": len(filtered_reservations)
        }

        return JsonResponse(response_data)


class UpdateInterestCategoriesView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'userId': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user'),
                'interestCate': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of interest category'),
                        }
                    ),
                    description='List of interest categories'
                ),
            },
            required=['userId', 'interestCate'],
        ),
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
            }
        )}
    )
    def post(self, request):
        user_id = request.data.get('userId')
        interest_categories = request.data.get('interestCate', [])

        user = get_object_or_404(CustomUser, id=user_id)

        category_objects = []
        for category_data in interest_categories:
            category_name = category_data.get('name')
            if category_name:
                category, created = InterestCategory.objects.get_or_create(name=category_name)
                category_objects.append(category)

        user.interest_categories.set(category_objects)
        user.save()

        return Response({"message": "Interest categories updated successfully."}, status=status.HTTP_200_OK)

class RemoveReservationView(APIView):
    def post(self, request, userId, boothID):
        user = get_object_or_404(CustomUser, id=userId)

        if user.reservation_status:
            updated_reservations = [
                reservation for reservation in user.reservation_status
                if reservation.get("boothid") != boothID
            ]
            user.reservation_status = updated_reservations
            user.save()

        booth = get_object_or_404(Booth, booth_id=boothID)
        if user in booth.queue.all():
            booth.queue.remove(user)
            booth.wait_time = booth.calculate_wait_time()
            booth.save()

        return Response({"message": "Reservation removed successfully."}, status=status.HTTP_200_OK)



class ResumeView(APIView):
    def get(self, request, userId):
        user = get_object_or_404(CustomUser, id=userId)
        experience_data = user.experience
        return Response({"experience": experience_data}, status=status.HTTP_200_OK)