from django.contrib.auth.models import AbstractUser
from django.db import models

class UserAccount(AbstractUser):
    image = models.URLField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True)
    about = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 

class Follower(models.Model):
    main_user = models.ForeignKey(UserAccount, related_name='followers', on_delete=models.CASCADE)
    follower = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='following_users')
    follower_username = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f'{self.follower_username} followed {self.main_user.username}'

class Following(models.Model):
    main_user = models.ForeignKey(UserAccount, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='followers_users')
    following_username = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.main_user.username} is following {self.following_username}'

