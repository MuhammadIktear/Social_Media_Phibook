from django.contrib import admin
from .models import UserAccount,Follower,Following
admin.site.register(UserAccount)
admin.site.register(Follower)
admin.site.register(Following)
# Register your models here.
