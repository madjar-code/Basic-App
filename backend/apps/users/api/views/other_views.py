from enum import Enum
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from users.models import User
from users.utils import (
    PasswordResetTokenGenerator,
)

from ..serializers import (
    AvatarSerializer,
    UserPasswordSerializer,
)


class RMessages(str, Enum):
    TOO_MANY_REQUESTS = 'Please wait more seconds before doing another request.'
    INCORRECT_PASSWORD = 'Password is not correct'
    NEED_CHANGE = 'You need to change at least 1 of the values.'
    USER_DELETED = 'Successfully deleted user.'
    INVALID_TOKEN = 'Given token is not valid'
    CANNOT_REGISTER = 'Cannot register user when already logged in.'


class UploadUserAvatar(APIView):
    """
    Upload avatar
    
    Upload an Avatar for current User
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, format=None):
        serializer = AvatarSerializer(data=request.data)
        
        if serializer.is_valid():
            user: User = request.user
            user.avatar = request.data.get('avatar')
            user.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetUserPassword(APIView):
    """ResetUserPassword"""
    permission_classes = (AllowAny,)

    def post(self, request: Request, token: str, uid: str, format=None):
        serializer = UserPasswordSerializer(data=request.data)
        uidb64 = force_str(urlsafe_base64_decode(uid))
        user: User = get_object_or_404(User, id=uidb64)
        token = PasswordResetTokenGenerator().check_token(user, token)
        
        if token:
            if serializer.is_valid():
                new_password = serializer.data.get('password')
                user.set_password(new_password)
                user.save()
                return Response(status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangeUserPassword(APIView):
    """Change user password"""

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request,  format=None):
        serializer = UserPasswordSerializer(data=request.data)

        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        if self.request.session.has_key('password_change'):
            delta: int = round((self.request.session['password_reset_email_sent'] + 600) -\
                datetime.now().timestamp())

            if delta > 0:
                return Response({
                    'Too Many Requests': RMessages.TOO_MANY_REQUESTS.value
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                self.request.session.pop('password_change')

        if serializer.is_valid():
            user: User = request.user
            if user.check_password(serializer.data.get('password')):
                password = serializer.data.get('new_password')
                user.set_password(password)
                user.save()
                self.request.session['password_change'] =\
                    datetime.now().timestamp()
                return Response(status=status.HTTP_201_CREATED)
            return Response({'detail': RMessages.INCORRECT_PASSWORD.value},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlacklistToken(APIView):
    """
    Logout User
    
    Logout current User and blacklist his JWT ``token``
    """
    
    permission_classes = (AllowAny,)
    
    @swagger_auto_schema(responses={
        200: openapi.Response(description='Ok'),
        400: openapi.Response(description='Bad Request'),
        403: openapi.Response(description='Forbidden')
    })
    def post(self, request: Request):
        current_user: User = request.user
        if current_user.is_authenticated:
            try:
                refresh_token = request.data['refresh_token']
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)
    