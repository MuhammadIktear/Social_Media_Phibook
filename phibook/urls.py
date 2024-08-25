from django.urls import path, include
from .import views

urlpatterns = [  
    path('allpost/', views.CreatePostSerializerView.as_view(), name='allpost'),
    path('<int:post_id>/like/', views.LikePostView.as_view(), name='like-post'),
    path('allpost/<int:pk>/', views.PostDetailView.as_view(), name='postdetail'),
    path('allcomment/', views.AllCommentsView.as_view(), name='allcomment'),
    
]