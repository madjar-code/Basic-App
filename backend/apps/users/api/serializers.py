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
    SAME_PASSWORDS = 'Passwords cannot be the same'

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

    def validate_username(self, value):
        username: str = self.get_initial().get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(RMessages.USERNAME_TAKEN.value)
        return value

    def validate_email(self, value):
        email: str = self.get_initial().get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(RMessages.EMAIL_TAKEN.value)
        return value

    def validate_password(self, value):
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


class AvatarSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar',)


class UserPasswordSerializer(ModelSerializer):
    password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'password',
            'new_password',
        )

    def validate_password(self, value):
        password: str = self.get_initial().get('password')
        new_password: str = self.get_initial().get('new_password')

        if password == new_password:
            raise ValidationError(RMessages.SAME_PASSWORDS.value)
        return value

    def validate_new_password(self, value):
        new_password: str = self.get_initial().get('new_password')
        if len(new_password) < 6:
            raise ValidationError(RMessages.SHORT_PASSWORD.value)
        return value


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'title',
            'avatar',
            'is_staff',
            'is_verified',
        )


class UserDetailsSerializer(ModelSerializer):
    username = serializers.CharField(min_length=3, allow_blank=True)
    email = serializers.EmailField(allow_blank=True)
    first_name = serializers.CharField(min_length=3, allow_blank=True)
    last_name = serializers.CharField(min_length=3, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
        )
