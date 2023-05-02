from enum import Enum
from datetime import datetime
from django.shortcuts import get_object_or_404
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
    send_email_delete_user,
    send_email_password_reset,
    send_email_verification,
)


class RMessages(str, Enum):
    TOO_MANY_REQUESTS = 'Please wait more seconds before\
                         doing another request.'


class SendEmailPasswordReset(APIView):
    """Send E-Mail"""
    permission_classes = (AllowAny,)
    
    def post(self, request: Request, email: str, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        # STOP user from spamming email verification
        if self.request.session.has_key('password_reset_email_sent'):
            delta: int = round((self.request.session['password_reset_email_sent'] + 600) -\
                datetime.now().timestamp())

            if delta > 0:
                return Response({
                    'Too Many Requests': RMessages.TOO_MANY_REQUESTS.value
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                self.request.session.pop('password_reset_email_sent')

        user: User = get_object_or_404(User, email=email)

        send_email_password_reset(request, user)
        self.request.session['password_reset_email_sent'] =\
            datetime.now().timestamp

        return Response(status=status.HTTP_200_OK)


class SendEmailVerification(APIView):
    """
    Send Email Verification
    
    Send an verification E-Mail to given User's ``email``
    """
    permission_classes = (AllowAny,)
    
    @swagger_auto_schema(responses={
        200: openapi.Response(description='Ok'),
        400: openapi.Response(description="Bad Request"),
        404: openapi.Response(description='Not Found'),
        429: openapi.Response(description="Too many Requests")
    })
    def post(self, request: Request, email: str, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.exists()

        # STOP user from spammin email verification
        if self.request.session.has_key('verification_email_sent'):
            delta = round((self.request.session['verification_email_sent'] +
                           600) - datetime.now().timestamp())
            if delta > 0:
                return Response({
                    'Too Many Requests': RMessages.TOO_MANY_REQUESTS.value
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                self.request.session.pop('verification_email_sent')
        user: User = get_object_or_404(User, email=email)

        if not user.is_verified:
            send_email_verification(request, user)
            self.request.session['verification_email_sent'] =\
                datetime.now().timestamp()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SendEmailDeleteUser(APIView):
    """Send Email to delete User account"""
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        # Stop user from spamming email to delete user account
        if self.request.session.has_key('delete_user_email_sent'):
            delta = round((self.request.session['delete_user_email_sent'] +
                           600) - datetime.now().timestamp())

            if delta > 0:
                return Response({
                        'Too Many Requests': RMessages.TOO_MANY_REQUESTS.value
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                self.request.session.pop('delete_user_email_sent')

        user: User = request.user
        if user.is_active:
            send_email_delete_user(request, user)
            self.request.session['delete_user_email_sent'] =\
                datetime.now().timestamp()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
