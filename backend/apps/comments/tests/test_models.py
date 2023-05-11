from typing import (
    NoReturn,
    TypeAlias,
)
from django.test import TestCase
from comments.models import Comment
from posts.models import Post
from users.models import User


class TestModels(TestCase):
    def setUp(self) -> None:
        self.user: User = User.objects.create_user(
            username='test', email='test@test.com', password='test')
        self.post: Post = Post.objects.create(
            title='Test Post', slug='test-post', thumbnail=\
            'https://www.test.example.com', author=self.user,
            body='Test content of the post', read_time=5, is_public=True)

    def test_comment_model(self) -> None | NoReturn:
        """
        New Comment does not change instance and is saved
        to Database.
        """
        comment: Comment = Comment.objects.create(
            post=self.post, author=self.user, body='Test comment body')

        self.assertIsInstance(comment, Comment)
        self.assertEqual(Comment.objects.all().first(), comment)
