from django.shortcuts import render
from rest_framework import viewsets
from .models import CreatePost,Comment,Like
from .serializers import CreatePostSerializer,AllComments,LikeSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django. http import Http404 
from accounts.models import UserAccount

class CreatePostSerializerView(APIView):
    serializer_class = CreatePostSerializer

    def get(self, request, format=None):
        user_id = self.request.query_params.get('userId')
        if user_id:
            posts = CreatePost.objects.filter(created_by=user_id).order_by('-created_at')
        else:
            posts = CreatePost.objects.all().order_by('-created_at')
        serializer = CreatePostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        print('Inside POST method')
        user_id = request.data.get('created_by')
        print(f'User ID: {user_id}')

        try:
            user = UserAccount.objects.get(id=user_id)
            print(f'User found: {user}')
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreatePostSerializer(data=request.data)
        print(f'Serializer data: {request.data}')
        print(f'Is serializer valid? {serializer.is_valid()}')
        
        if serializer.is_valid():
            serializer.save(created_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print(f'Serializer errors: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetailView(APIView):
    def get_object(self, pk):
        try:
            return CreatePost.objects.get(pk=pk)
        except CreatePost.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = CreatePostSerializer(post)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        print('inside put method')
        post = self.get_object(pk)
        serializer = CreatePostSerializer(post, data=request.data, partial=True) 
        print(serializer)
        print(serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            print('VALIDATED')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class AllCommentsView(APIView):
    serializer_class = AllComments
    def get(self, request, format=None):
        comment_id = request.query_params.get('comment_id')
        
        if comment_id:
            posts = Comment.objects.filter(id=comment_id)
            
            serializer = AllComments(posts, many=True)
            return Response(serializer.data)
       
        else:
            posts = Comment.objects.all()
            serializer = AllComments(posts, many=True)
            return Response(serializer.data)



    def post(self, request, format=None):
        serializer = AllComments(data=request.data)
        user_id = request.data.get('user')

        try:
            user = UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def put(self, request, format=None):
        comment_id = request.data.get('id')
        if not comment_id:
            return Response({'error': 'Comment ID is required for updating'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AllComments(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print("updated")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, format=None):
        comment_id = request.query_params.get('comment_id')
        if not comment_id:
            return Response({'error': 'Comment ID is required for deletion'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikePostView(APIView):
    serializer_class = LikeSerializer

    def post(self, request, post_id):
        user_id = request.data.get('userId')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        existing_like = Like.objects.filter(likepost=post_id, user=user).first()

        if existing_like:
            existing_like.delete()
            like_count = Like.objects.filter(likepost=post_id).count()
            return Response({'message': 'Like removed', 'like_count': like_count}, status=status.HTTP_200_OK)
        else:
            data = {
                'likepost': post_id,
                'user': user.id
            }
            serializer = LikeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                like_count = Like.objects.filter(likepost=post_id).count()
                return Response({'message': 'Like added', 'like_count': like_count}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        user_id = request.data.get('userId')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        existing_like = Like.objects.filter(likepost=post_id, user=user).first()

        if existing_like:
            existing_like.delete()
            like_count = Like.objects.filter(likepost=post_id).count()
            return Response({'message': 'Like removed', 'like_count': like_count}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)