from django.db import models
from accounts.models import UserAccount

# Create your models here.
class ContactUs(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    name=models.CharField(max_length=40)
    email=models.CharField(max_length=50)
    message=models.TextField()
    
    def __str__(self):
        return self.email
    class Meta:
        verbose_name_plural="Contact Us"