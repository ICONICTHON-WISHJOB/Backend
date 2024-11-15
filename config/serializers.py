from rest_framework import serializers
from users.models import CustomUser, InterestCategory

class InterestCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestCategory
        fields = ['id', 'name']

class CustomUserSerializer(serializers.ModelSerializer):
    interest_categories = InterestCategorySerializer(many=True)  # Many-to-Many 관계를 처리

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'phoneNum', 'birth', 'full_name', 'school',
            'department', 'admission_date', 'graduation_date', 'experience',
            'self_introduction', 'companies_of_interest', 'reservation_status', 'interest_categories'
        ]
