# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from . import serializers
from accounts.models import UserAccount
import logging

class ContactUsViewset(APIView):
    serializer_class = serializers.ContactUsSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        user_id = request.data.get('user')

        try:
            user = UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            serializer.save(user=user)
            self.send_email(serializer.validated_data)
            return Response({'message': 'Message sent successfully'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_email(self, contact_data):
        subject = 'Received Contact Message'
        message = f"""
        Hello,

        You have received a new contact message.

        Details:
        Name: {contact_data.get('name')}
        Email: {contact_data.get('email')}
        Message: {contact_data.get('message')}

        Best Regards,
        Phibook Team
        """

        recipient_email = settings.EMAIL_HOST_USER

        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient_email],
                fail_silently=False,
            )
        except Exception as e:
            logging.error(f"Error sending email: {e}")
