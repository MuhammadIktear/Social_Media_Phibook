from django.db import models
from accounts.models import UserAccount

class CreatePost(models.Model):
    image = models.URLField(max_length=200, blank=True, null=True)
    video = models.URLField(max_length=200, blank=True, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='created_posts')

    def __str__(self):
        return f'post created by {self.created_by.username}'

class Like(models.Model):
    likepost = models.ForeignKey(CreatePost, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)

    def __str__(self):
        return f'Liked by {self.user.username}'

class Comment(models.Model):
    commentpost = models.ForeignKey(CreatePost, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f'comment by {self.user.username}'
  