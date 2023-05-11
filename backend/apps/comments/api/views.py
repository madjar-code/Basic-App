from enum import Enum
from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from users.models import User
from posts.models import Post
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer, CreateCommentSerializer
)


class RMessages(str, Enum):
    TOO_MANY_REQUESTS = 'Please wait more seconds before sending\
                        another comment.'
    VERIFICATION_PROBLEM = 'Please activate your account first.'


class CommentsList(APIView):
    """
    List of Comments
    
    Return a list of all **Comments** that
    belong to Post with give ``slug``
    """

    @swagger_auto_schema(responses={200: CommentSerializer(many=True),
                                    404: openapi.Response(description='Not Found')})
    def get(self, request: Request, slug: str) -> Response:
        post = get_object_or_404(Post, slug=slug)

        comments = Comment.objects.filter(post_id=post.id)
        data = CommentSerializer(comments, many=True).data

        return Response(data, status=status.HTTP_200_OK)


class CreateComment(APIView):
    """
    Create Comment
    
    Create comment under the post with the five ``slug``
    """

    @swagger_auto_schema(request_body=CreateCommentSerializer(),
                         responses={200: CommentSerializer(),
                                    400: openapi.Response(description='Serializer error',
                                                          examples={'application/json': CreateCommentSerializer().error_messages}),
                                    403: openapi.Response(description='Forbidden'),
                                    404: openapi.Response(description='Not Found'),
                                    429: openapi.Response(description='Too Many Requests')})
    def post(self, request: Request, slug: str) -> Response:
        serializer = CreateCommentSerializer(data=request.data)
        current_user: User = request.user

        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        if self.request.session.has_key('comment_posted'):
            delta = round((self.request.session['comments_posted'] + 600 -\
                datetime.now().timestamp()))
            if delta > 0:
                return Response({'Too Many Requests': RMessages.TOO_MANY_REQUESTS.value},
                                status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                self.request.session.pop('comment_posted')

        if serializer.is_valid():
            if current_user.is_verified:
                post = get_object_or_404(Post, slug=slug, is_public=True)
                body = serializer.data.get('body')

                comment = Comment.objects.create(
                    author=current_user, post=post, body=body)

                self.request.session['comment_posted'] =\
                    datetime.now().timestamp()
                return Response(CommentSerializer(comment).data,
                                status=status.HTTP_201_CREATED)
            return Response({'detail': RMessages.VERIFICATION_PROBLEM.value},
                            status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)