from django.contrib import admin
from .models import CreatePost,Comment,Like
admin.site.register(CreatePost)
admin.site.register(Comment)
admin.site.register(Like)
# Register your models here.
