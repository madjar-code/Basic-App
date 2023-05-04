from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from users.api.serializers import UserSerializer

from comments.models import Comment


class CommentSerializer(ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = (
            'id',
            'author',
            'body',
            'created_at',
        )


class CreateCommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ('body',)
