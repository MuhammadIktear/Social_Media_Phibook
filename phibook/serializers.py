from rest_framework import serializers
from .models import CreatePost, Like, Comment

class AllComments(serializers.ModelSerializer):
    class Meta:
        model=Comment
        read_only_fields=['user']
        fields='__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Like
        fields='__all__'

class CreatePostSerializer(serializers.ModelSerializer):
    comments = AllComments(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)

    class Meta:
        model = CreatePost
        fields = '__all__'    
        read_only_fields = ['created_at', 'created_by']