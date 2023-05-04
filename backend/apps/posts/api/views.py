from enum import Enum
from typing import (
    Any,
)
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from posts.models import Post
from posts.api.serializers import PostSerializer


class BooleanType(str, Enum):
    TRUE = 'true'
    FALSE = 'false'


class PostList(ListAPIView):
    """
    List of Posts
    
    Return a list of all **Posts** from database.
    
    Optional query parameters:
    ``recent`` - If ``true`` return only the **4** most recent
    **Posts**
    """
    def get_queryset(self) -> QuerySet:
        request: Request = self.request
        recent: BooleanType | None = request.query_params.get('recent')
        if recent == BooleanType.TRUE.value:
            return Post.objects.all()[:4]
        return Post.objects.all()

    @swagger_auto_schema(responses={200, PostSerializer(many=True)})
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)


class PostDetail(APIView):
    """
    Detailed Post
    
    Return a detailed info about a **Post** with given ``slug``
    """
    @swagger_auto_schema(responses={200: PostSerializer(), 404: openapi.Response(description='Not Found')})
    def get(self, request: Request, slug: str) -> Response:
        post = get_object_or_404(Post, slug=slug)

        data = PostSerializer(post).data
        return Response(data, status=status.HTTP_200_OK)
