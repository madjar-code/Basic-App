from typing import (
    NoReturn,
)
from django.core import mail
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import (
    APIRequestFactory, APITestCase
)
from users.models import User
from users.utils import (
    DeleteAccountTokenGenerator,
    EmailTokenGenerator,
    PasswordResetTokenGenerator,
    send_email_delete_user,
    send_email_password_reset,
    send_email_verification,
)


class TestUtils(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test', email='test@test.com', password='strongpassword')
        self.request = APIRequestFactory().request()

    def test_email_token_generator(self) -> None | NoReturn:
        """Email Token stays the same after it's decode"""
        token: str = EmailTokenGenerator().make_token(self.user)
        token_decoded: bool = EmailTokenGenerator().check_token(self.user, token)
        
        self.assertTrue(token_decoded)

    def test_password_reset_token_generator(self) -> None | NoReturn:
        """Password Reset Token stays the same after it's decode"""
        token: str = PasswordResetTokenGenerator().make_token(self.user)
        token_decoded: bool = PasswordResetTokenGenerator().\
            check_token(self.user, token)
        
        self.assertTrue(token_decoded)

    def test_delete_acc_token_generator(self) -> None | NoReturn:
        """Delete Account Token stays the same after It's decoded"""
        token: str = DeleteAccountTokenGenerator().make_token(self.user)
        token_decoded: bool = DeleteAccountTokenGenerator().\
            check_token(self.user, token)

        self.assertTrue(token_decoded)

    def test_send_email_verification(self) -> None | NoReturn:
        """
        E-Mail with email verification is sent with every 
        important information.
        """
        send_email_verification(self.request, self.user)
        
        email: EmailMessage = mail.outbox[0]
        uid = urlsafe_base64_encode(force_bytes(self.user.id))
        token = EmailTokenGenerator().make_token(self.user)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(email.to[0], self.user.email)
        self.assertEqual(email.subject, 'Basic App - Activate your account')
        self.assertIn(self.user.username, email.body)
        self.assertIn(uid, email.body)
        self.assertIn(token, email.body)

    def test_send_email_password_reset(self) -> None | NoReturn:
        """
        E-Mail with password reset is sent with every
        important information
        """
        send_email_password_reset(self.request, self.user)
        
        email: EmailMessage = mail.outbox[0]
        uid = urlsafe_base64_encode(force_bytes(self.user.id))
        token = PasswordResetTokenGenerator().make_token(self.user)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(email.to[0], self.user.email)
        self.assertEqual(
            email.subject, 'Basic App - Reset your password')
        self.assertIn(self.user.username, email.body)
        self.assertIn(uid, email.body)
        self.assertIn(token, email.body)
    
    def test_send_email_delete_user(self) -> None | NoReturn:
        """
        E-Mail with account removal is sent with every
        important information
        """
        send_email_delete_user(self.request, self.user)
        
        email: EmailMessage = mail.outbox[0]
        uid = urlsafe_base64_encode(force_bytes(self.user.id))
        token = DeleteAccountTokenGenerator().make_token(self.user)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(email.to[0], self.user.email)
        self.assertEqual(
            email.subject, 'Basic App - Delete your account')
        self.assertIn(self.user.username, email.body)
        self.assertIn(uid, email.body)
        self.assertIn(token, email.body)
