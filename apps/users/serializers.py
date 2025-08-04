from rest_framework import serializers
from .models import User, EmployeeProfile, EmployerProfile

class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'password',
            'email',
            'bio',
            'role',
            'birth_date',
            'phone_number',
            'is_active',
            'profile_pic',
            'date_joined'
        ]
        read_only_fields = ['id', 'role', 'is_active', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True, 'style':{'input_type': 'password'}},
            'profile_pic': {'required': False}
        }

    def validate_bio(self, value):
        if len(value) > 500:
            raise serializers.ValidationError(
                "Bio can't have more than 500 characters."
            )
        return value
        
    def validate_role(self, value):
        if value not in ['admin', 'employee', 'employer']:
            raise serializers.ValidationError(
                "Role is not valid."
            )
        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password needs to have at least 8 characters"
            )
        if not any(c.isalpha() for c in value) and not any(c.isdigit() for c in value):
            raise serializers.ValidationError(
                "Password needs at least one letter and number"
            )
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email already registered."
            )
        return value
            
    def validate_phone_number(self, value):
        if not all(value.isdigit()):
            raise serializers.ValidationError(
                "Phone number is not valid."
            )
        return value
        
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                "The passwords do not match."
            )
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user