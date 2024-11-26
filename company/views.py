from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import Booth, Company, CustomUser

class WaitCountView(APIView):
    @swagger_auto_schema(
        operation_summary="Get wait count for a specific booth by company ID",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the company associated with the booth",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Wait count response",
                examples={
                    "application/json": {
                        "waitCnt": 4
                    }
                }
            ),
            404: "Booth or Company not found"
        }
    )
    def get(self, request, id):
        try:
            company = Company.objects.get(id=id)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        booth = Booth.objects.filter(company=company).first()
        if not booth:
            return Response({"error": "Booth not found for the given company"}, status=status.HTTP_404_NOT_FOUND)

        wait_count = booth.queue.count()
        return Response({"waitCnt": wait_count}, status=status.HTTP_200_OK)


class WaitListView(APIView):
    @swagger_auto_schema(
        operation_summary="Get wait list for a specific booth by company ID",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the company associated with the booth",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Wait list response",
                examples={
                    "application/json": {
                        "users": [
                            {
                                "user_id": "test@example.com",
                                "full_name": "김도현",
                            },
                            {
                                "user_id": "test2@example.com",
                                "full_name": "박지수",
                            }
                        ],
                        "totalCnt": 2
                    }
                }
            ),
            404: "Booth or Company not found"
        }
    )
    def get(self, request, id):
        try:
            company = Company.objects.get(id=id)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        booth = Booth.objects.filter(company=company).first()
        if not booth:
            return Response({"error": "Booth not found for the given company"}, status=status.HTTP_404_NOT_FOUND)

        users_in_queue = booth.queue.all()
        user_data = [
            {
                "user_id": user.email,
                "full_name": user.full_name
            }
            for user in users_in_queue
        ]

        # Prepare the response
        response_data = {
            "users": user_data,
            "totalCnt": users_in_queue.count()
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ConsultationDoneView(APIView):
    @swagger_auto_schema(
        operation_description="Marks a consultation as completed for a user in the booth's queue and updates both the company and user consultation records.",

        responses={
            200: openapi.Response(
                description="Consultation completed successfully",
                examples={
                    "application/json": {
                        "message": "Consultation completed successfully",
                        "consulted_user": {
                            "user_id": "test@example.com",
                            "full_name": "김도현"
                        },
                        "company": {
                            "company_id": "A12@company.com",
                            "company_name": "Company A"
                        }
                    }
                }
            ),
            404: openapi.Response(
                description="Not found",
                examples={
                    "application/json": {"error": "Invalid company_id or User not found in queue"}
                }
            ),
        }
    )
    def post(self, request, id):
        company_id = request.session['id']

        try:
            company = Company.objects.get(company_id=company_id)
            print(company)
        except Company.DoesNotExist:
            return Response({"error": "Invalid company_id"}, status=status.HTTP_404_NOT_FOUND)
        booth = company.booths.first()
        if not booth:
            return Response({"error": "Booth not found for this company"}, status=status.HTTP_404_NOT_FOUND)
        try:
            user = booth.queue.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found in queue"}, status=status.HTTP_404_NOT_FOUND)

        company.completed_consultations.add(user)

        booth.queue.remove(user)

        company.save()
        user.save()

        return Response({
            "message": "Consultation completed successfully",
            "consulted_user": {
                "user_id": user.email,
                "full_name": user.full_name,
            },
            "company": {
                "company_id": company.company_id,
                "company_name": company.name,
            }
        }, status=status.HTTP_200_OK)



class ConsultDeleteView(APIView):
        @swagger_auto_schema(
            operation_description="Deletes a user from the company's booth queue",
            manual_parameters=[
                openapi.Parameter(
                    'id', openapi.IN_PATH, description="User ID to delete from queue", type=openapi.TYPE_STRING
                )
            ],
            responses={
                200: openapi.Response(
                    description="User removed from queue successfully",
                    examples={
                        "application/json": {
                            "message": "User removed from queue successfully"
                        }
                    }
                ),
                404: openapi.Response(
                    description="Not found",
                    examples={
                        "application/json": {"error": "User or Company not found"}
                    }
                ),
            }
        )
        def post(self, request, id):
            company_id = request.session.get('id')
            if not company_id:
                return Response({"error": "Company ID not found in session"}, status=status.HTTP_404_NOT_FOUND)

            try:
                company = Company.objects.get(company_id=company_id)
            except Company.DoesNotExist:
                return Response({"error": "Invalid company_id"}, status=status.HTTP_404_NOT_FOUND)

            booth = company.booths.first()
            if not booth:
                return Response({"error": "Booth not found for this company"}, status=status.HTTP_404_NOT_FOUND)

            try:
                user = booth.queue.get(id=id)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found in queue"}, status=status.HTTP_404_NOT_FOUND)

            booth.queue.remove(user)

            return Response({
                "message": "User removed from queue successfully"
            }, status=status.HTTP_200_OK)

class CompletedConsultationsListView(APIView):
    def post(self, request):
        company_id = request.session['id']
        print(request.session)
        if not company_id:
            return Response({"error": "Company ID not found in session"}, status=status.HTTP_404_NOT_FOUND)

        try:
            company = Company.objects.get(company_id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        completed_users = company.completed_consultations.all()
        users_data = [
            {
                "user_id": user.email,
                "full_name": user.full_name
            }
            for user in completed_users
        ]

        response_data = {
            "users": users_data,
            "totalCnt": len(users_data)
        }

        return Response(response_data, status=status.HTTP_200_OK)