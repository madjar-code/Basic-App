from typing import (
    NoReturn,
)
from django.test.testcases import TestCase
from users.models import User
from comments.api.serializers import (
    CommentSerializer,
    CreateCommentSerializer
)


class TestSerializers(TestCase):
    def setUp(self) -> None:
        self.user: User = User.objects.create_user(
            username='test', email='test@test.com', password='test')
        self.comment_serializer = CommentSerializer(
            data={'author': self.user, 'body': 'Test Body'})
        self.create_comment_serializer = CreateCommentSerializer(
            data={'body': 'Test Body'})

    def test_comment_serializer(self) -> None | NoReturn:
        """Comment Serializer"""

        serializer: CommentSerializer = self.comment_serializer
        self.assertTrue(serializer.is_valid())
        data = serializer.data

        self.assertCountEqual(data.keys(), ['body'])
        self.assertEqual(data['body'], 'Test Body')

    def test_create_comment_serializer(self) -> None | NoReturn:
        """Create Comment Serializer"""
        serializer: CreateCommentSerializer = self.create_comment_serializer
        self.assertTrue(serializer.is_valid())
        data = serializer.data
        
        self.assertCountEqual(data.keys(), ['body'])
        self.assertEqual(data['body'], 'Test Body')
