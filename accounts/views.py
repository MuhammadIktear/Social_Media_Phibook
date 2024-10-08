from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet
from .models import UserAccount, Follower, Following
from .serializers import RegistrationSerializer, UserLoginSerializer, FollowerSerializer, FollowingSerializer,UserSerializer
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework import generics, status
from django.contrib.auth.hashers import check_password
from .models import UserAccount
from .serializers import PasswordChangeSerializer


class UserRegistrationsApiView(APIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data.get('email')
        if UserAccount.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists."}, status=400)
        if serializer.is_valid():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = f'https://phibook-f17w.onrender.com/user/activate/{uid}/{token}/'
            email_subject = "Confirm Your Email"
            email_body = render_to_string('confirm_email.html', {'confirm_link': confirm_link})
            email = EmailMultiAlternatives(email_subject, '', to=[user.email])
            email.attach_alternative(email_body, "text/html")
            email.send()
            return Response("Check your email for confirmation")
        return Response(serializer.errors, status=400)


def activate_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserAccount._default_manager.get(pk=uid)
    except (UserAccount.DoesNotExist, TypeError, ValueError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('https://phibook.netlify.app/login')
    else:
        return redirect('https://phibook.netlify.app/register')


class UserLoginApiView(APIView):
    serializer_class = UserLoginSerializer
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)

            if user:
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)
                request.session['user_id'] = user.id
                return Response({'token': token.key, 'user_id': user.id})
            else:
                return Response({'error': "Invalid Credentials"}, status=400)
        return Response(serializer.errors, status=400)


class UserLogoutView(APIView):
    def get(self, request):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=200)
    

class UserAccountViewSet(ModelViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['username', 'first_name', 'last_name']


class AllFollowerView(APIView):
    serializer_class = FollowerSerializer

    # Get all followings for a specific user
    def get(self, request, format=None):
        user_id = request.query_params.get('user_id')
        
        if user_id:
            try:
                user = UserAccount.objects.get(id=user_id)
            except UserAccount.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            followers = Follower.objects.filter(main_user=user)
            serializer = FollowerSerializer(followers, many=True)
            return Response(serializer.data)
        
        return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
    # Follow a user
    def post(self, request, format=None):
        main_user_id = request.data.get('main_user')
        follower_id = request.data.get('follower')

        try:
            main_user = UserAccount.objects.get(id=main_user_id)
            follower_user = UserAccount.objects.get(id=follower_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if Follower.objects.filter(main_user=main_user, follower=follower_user).exists():
            return Response({'error': 'Already following this user.'}, status=status.HTTP_400_BAD_REQUEST)

        follower = Follower(main_user=main_user, follower=follower_user)
        follower.save()

        serializer = FollowerSerializer(follower)
        return Response(serializer.data, status=status.HTTP_201_CREATED)    

    # remove follower
    def delete(self, request, format=None):
        main_user_id = request.query_params.get('main_user')
        follower_id = request.query_params.get('follower')

        if not main_user_id or not follower_id:
            return Response({'error': 'Main user ID and follower ID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            main_user = UserAccount.objects.get(id=main_user_id)
            follower_user = UserAccount.objects.get(id=follower_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            followers = Follower.objects.get(main_user=main_user, follower=follower_user)
        except Follower.DoesNotExist:
            return Response({'error': 'Follower relationship not found.'}, status=status.HTTP_404_NOT_FOUND)

        followers.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AllFollowingView(APIView):
    serializer_class = FollowingSerializer

    # Get all followings for a specific user
    def get(self, request, format=None):
        user_id = request.query_params.get('user_id')
        
        if user_id:
            try:
                user = UserAccount.objects.get(id=user_id)
            except UserAccount.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            followings = Following.objects.filter(main_user=user)
            serializer = FollowingSerializer(followings, many=True)
            return Response(serializer.data)
        
        return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Follow a user
    def post(self, request, format=None):
        main_user_id = request.data.get('main_user')
        following_id = request.data.get('following')

        try:
            main_user = UserAccount.objects.get(id=main_user_id)
            following_user = UserAccount.objects.get(id=following_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if Following.objects.filter(main_user=main_user, following=following_user).exists():
            return Response({'error': 'Already following this user.'}, status=status.HTTP_400_BAD_REQUEST)

        following = Following(main_user=main_user, following=following_user)
        following.save()

        serializer = FollowingSerializer(following)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Unfollow a user
    def delete(self, request, format=None):
        main_user_id = request.query_params.get('main_user')
        following_id = request.query_params.get('following')

        if not main_user_id or not following_id:
            return Response({'error': 'Main user ID and following ID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            main_user = UserAccount.objects.get(id=main_user_id)
            following_user = UserAccount.objects.get(id=following_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            following = Following.objects.get(main_user=main_user, following=following_user)
        except Following.DoesNotExist:
            return Response({'error': 'Following relationship not found.'}, status=status.HTTP_404_NOT_FOUND)

        following.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class PasswordChangeView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer

    def update(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        try:
            user = UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.data.get("old_password")
            if not check_password(old_password, user.password):
                return Response({"old_password": "Wrong password."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    

from django_rest_passwordreset.views import ResetPasswordRequestToken
class CustomResetPasswordRequestToken(ResetPasswordRequestToken):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f'https://phibook.netlify.app/reset-password-confirm.html?uid={uid}&token={token}'

        email_subject = "Reset Your Password"
        email_body = render_to_string('password_reset_email.html', {'reset_link': reset_link})
        email_message = EmailMultiAlternatives(email_subject, '', to=[email])
        email_message.attach_alternative(email_body, "text/html")
        email_message.send()
        
        return Response({"detail": "Check your email for password reset instructions."}, status=status.HTTP_200_OK)


class CustomResetPasswordConfirm(APIView):
    def put(self, request, *args, **kwargs):
        uidb64 = request.query_params.get('uid')
        token = request.query_params.get('token')

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = UserAccount.objects.get(id=user_id)
        except (TypeError, ValueError, OverflowError, UserAccount.DoesNotExist):
            return Response({'error': 'Invalid user or token.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid token or token has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'error': 'New password is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
        

