from rest_framework import serializers
from .models import UserAccount, Follower, Following

class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserAccount
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data['is_active'] = False
        return UserAccount.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    
    
class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = ['id', 'main_user', 'follower', 'follower_username']
class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Following
        fields = ['id', 'main_user', 'following', 'following_username']        

class UserSerializer(serializers.ModelSerializer):
    followers = FollowerSerializer(many=True, read_only=True)
    following = FollowingSerializer(many=True, read_only=True)

    class Meta:
        model = UserAccount
        fields = ['id', 'username', 'first_name','last_name','email', 'image' ,'created_at', 'bio', 'about', 'followers','following']    
        

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)





