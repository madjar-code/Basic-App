from enum import Enum
from typing import (
    Optional,
    Dict,    
)
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
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from users.models import User
from users.utils import (
    DeleteAccountTokenGenerator,
    send_email_verification,
)
from ..serializers import (
    UserSerializer,
    UserDetailsSerializer,
    CreateUserSerializer,
)


class RMessages(str, Enum):
    TOO_MANY_REQUESTS = 'Please wait more seconds before doing another request.'
    INCORRECT_PASSWORD = 'Password is not correct'
    NEED_CHANGE = 'You need to change at least 1 of the values.'
    USER_DELETED = 'Successfully deleted user.'
    INVALID_TOKEN = 'Given token is not valid'
    CANNOT_REGISTER = 'Cannot register user when already logged in.'


class CreateUser(APIView):
    """
    Create User
    
    Create user ther send him an e-mail with link to verification.
    """
    permission_classes = (AllowAny,)
    
    @swagger_auto_schema(
        request_body=CreateUserSerializer(),
        responses={
            200: UserSerializer(),
            400: openapi.Response(
                description='Serializer error',
                examples={'application/json': CreateUserSerializer().error_messages}),
            403: openapi.Response(description='Forbidden')
    })
    def post(self, request: Request):
        current_user: User = request.user
        if not current_user.is_authenticated:
            serializer = CreateUserSerializer(data=request.data)

            if serializer.is_valid():
                user: User = serializer.save()
                if user:
                    send_email_verification(request, user)

                    return Response(UserSerializer(user).data,
                                    status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({'Forbidden': RMessages.CANNOT_REGISTER.value},
                            status=status.HTTP_403_FORBIDDEN)


class GetCurrentUser(APIView):
    """
    Current User
    
    Return an information about the current logged in user.
    """
    permission_classes = (IsAuthenticated,)
    
    @swagger_auto_schema(responses={200: UserSerializer()})
    def get(self, request: Request, format=None):
        user: User = request.user

        return Response({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'title': user.title,
            'avatar': user.avatar.url,
            'is_staff': user.is_staff,
            'is_verified': user.is_verified
        })


class ChangeUserDetails(APIView):
    """Change User personal details"""
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, format=None):
        serializer = UserDetailsSerializer(data=request.data)

        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        if self.request.session.has_key('details_change'):
            delta = round((self.request.session['details_change'] + 600) -\
                datetime.now().timestamp())

            if delta > 0:
                return Response({
                    'Too Many Requests': RMessages.TOO_MANY_REQUESTS.value
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                self.request.session.pop('details_change')

        if serializer.is_valid():
            is_changed: bool = False
            user: User = request.user

            data: Dict = serializer.data
            
            username: Optional[str] = data.get('username')
            email: Optional[str] = data.get('email')
            first_name: Optional[str] = data.get('first_name')
            last_name: Optional[str] = data.get('last_name')
            
            if username or email or first_name or last_name:
                is_changed = True
            if username:
                user.username = username
            if email:
                user.email = email
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name

            if is_changed:
                user.save()
                self.request.session['details_change'] =\
                    datetime.now().timestamp()
                return Response(status=status.HTTP_201_CREATED)
            return Response({'detail': RMessages.NEED_CHANGE.value},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUser(APIView):
    """
    Delete User account
    
    Delete a User with given ``UID`` and ``Token``
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, token: str, uid: str) -> Response:
        uidb64 = force_str(urlsafe_base64_decode(uid))

        user = get_object_or_404(User, id=uidb64)
        token = DeleteAccountTokenGenerator().check_token(user, token)

        if token:
            user.delete()
            return Response({'Deleted': RMessages.USER_DELETED.value},
                            status=status.HTTP_201_CREATED)
        return Response({'Invalid Token': RMessages.INVALID_TOKEN},
                        status=status.HTTP_406_NOT_ACCEPTABLE)
