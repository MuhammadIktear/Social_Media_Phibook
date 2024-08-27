from django.urls import path
from . import views
urlpatterns=[
    path('',views.ContactUsViewset.as_view(),name='contact'),
]