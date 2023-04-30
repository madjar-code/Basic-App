from __future__ import annotations
from enum import Enum
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from common.mixins.models import UUIDModel


class ErrorMessages(str, Enum):
    NO_USERNAME = 'User needs to have an username'
    NO_EMAIL = 'User needs to have an email'
    NO_PASSWORD = 'User needs to have a password'


class UserManager(BaseUserManager):
    def create_user(self, username: str, email: str, password: str,
                    first_name: str = None, last_name: str = None) -> User:
        if not username:
            raise ValueError(ErrorMessages.NO_USERNAME.value)
        if not email:
            raise ValueError(ErrorMessages.NO_EMAIL.value)
        if not password:
            raise ValueError(ErrorMessages.NO_PASSWORD.value)

        email: str = self.normalize_email(email)
        user: User = self.model(username=username, email=email,
                                first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username: str, email: str, password: str,
                    first_name: str = None, last_name: str = None) -> User:
        user: User = self.create_user(username, email=self.normalize_email(email),
                                first_name=first_name, last_name=last_name,
                                password=password)
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save()
        
        return user


class User(UUIDModel, AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(
        upload_to='avatars', default='avatars/default.png')
    title = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email', 'first_name', 'last_name')
    
    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'{self.username} - {self.email}'
