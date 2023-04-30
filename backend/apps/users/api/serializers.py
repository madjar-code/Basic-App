from enum import Enum
from typing import (
    Dict,
)
from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
)
from users.models import User


class RMessages(str, Enum):
    USERNAME_TAKEN = 'This username is already taken.'
    EMAIL_TAKEN = 'This email is already taken'    
    SHORT_PASSWORD = 'Password need to be at least 6 characters long'


class CreateUserSerializer(ModelSerializer):
    username = serializers.CharField(min_length=3, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=6, write_only=True)
    first_name = serializers.CharField(
        min_length=3, required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        min_length=3, required=False, allow_blank=True
    )
    
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
        )

    def validate_username(self, value: Dict) -> Dict:
        username: str = self.get_initial().get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(RMessages.USERNAME_TAKEN.value)
        return value

    def validate_email(self, value: Dict) -> Dict:
        email: str = self.get_initial().get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(RMessages.EMAIL_TAKEN.value)
        return value

    def validate_password(self, value: Dict) -> Dict:
        password = self.get_initial().get('password')
        if len(password) < 6:
            raise ValidationError(RMessages.SHORT_PASSWORD.value)
        return value

    def create(self, validated_data: Dict) -> User:
        password: str = validated_data.pop('password', None)
        
        user: User = self.Meta.model(**validated_data)
        
        if password:
            user.set_password(password)
        
        user.save()
        return user
