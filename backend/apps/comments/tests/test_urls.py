from django.test import TestCase
from django.urls import resolve
from comments.api.views import (
    CommentsList,
    CreateComment,
)


class TestUrls(TestCase):
    def test_comments_list_url(self):
        """
        Url is corresponding to CommentsList view
        """
        url = resolve('/api/comments/test/')
        self.assertEqual(url.func.cls, CommentsList)

    def test_create_comment_url(self):
        """
        Url is corresponding to CreateComment view
        """
        url = resolve('/api/comments/test/send/')
        self.assertEqual(url.func.cls, CreateComment)
