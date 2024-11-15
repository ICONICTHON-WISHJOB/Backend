
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from users.models import CustomUser, Company, Booth, BoothQueue, InterestCategory
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.http import JsonResponse






class MyPageView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, userId):
        # 사용자 정보 가져오기
        user = get_object_or_404(CustomUser, id=userId)

        # 관심 있는 회사 가져오기
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
        # 사용자를 가져옵니다.
        user = get_object_or_404(CustomUser, id=userId)

        # 관심 직무 목록을 가져옵니다.
        interest_categories = user.interest_categories.all()
        interest_category_names = [category.name for category in interest_categories]

        # 관심 직무 이름 목록을 반환합니다.
        response_data = {
            "interest_categories": interest_category_names
        }
        return JsonResponse(response_data)


class ReservationListView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, userId, doneType=None):
        # userId로 사용자 가져오기
        user = get_object_or_404(CustomUser, id=userId)

        # 상담 기록 가져오기
        reservation_status = user.reservation_status or []

        # doneType이 제공되었는지 확인하고, 필터링 수행
        if doneType is not None:
            filtered_reservations = [
                reservation for reservation in reservation_status if reservation.get("doneType") == doneType
            ]
        else:
            filtered_reservations = reservation_status  # doneType이 없으면 전체 기록 반환

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

        # 사용자 가져오기
        user = get_object_or_404(CustomUser, id=user_id)

        # 관심 직무 목록 갱신
        category_objects = []
        for category_data in interest_categories:
            category_name = category_data.get('name')
            if category_name:
                # 관심 직무가 존재하지 않는다면 새로 생성
                category, created = InterestCategory.objects.get_or_create(name=category_name)
                category_objects.append(category)

        # 사용자 관심 직무 설정
        user.interest_categories.set(category_objects)
        user.save()

        return Response({"message": "Interest categories updated successfully."}, status=status.HTTP_200_OK)





class RemoveReservationView(APIView):
    def post(self, request, userId, boothID):
        # 사용자 가져오기
        user = get_object_or_404(CustomUser, id=userId)

        # 사용자의 예약 내역에서 해당 부스 예약 제거
        if user.reservation_status:
            updated_reservations = [
                reservation for reservation in user.reservation_status
                if reservation.get("boothid") != boothID  # boothID를 가진 예약만 제거
            ]
            # 예약 내역 업데이트
            user.reservation_status = updated_reservations
            user.save()

        # 부스의 대기열에서도 사용자 제거
        booth = get_object_or_404(Booth, booth_id=boothID)
        if user in booth.queue.all():
            booth.queue.remove(user)
            booth.wait_time = booth.calculate_wait_time()  # 대기 시간을 다시 계산
            booth.save()

        return Response({"message": "Reservation removed successfully."}, status=status.HTTP_200_OK)



class ResumeView(APIView):
    def get(self, request, userId):
        # 사용자 정보 가져오기
        user = get_object_or_404(CustomUser, id=userId)

        # 경력 필드 반환
        experience_data = user.experience

        # 응답 생성
        return Response({"experience": experience_data}, status=status.HTTP_200_OK)