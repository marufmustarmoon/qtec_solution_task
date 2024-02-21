from django.urls import path
from .views import UserLoginAPIView,BlogListCreateAPIView,UserRegistrationAPIView,BlogSearchAPIView,BlogDetailAPIView,BookmarkAPIView


urlpatterns = [
    path('api/register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('api/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('blogs/', BlogListCreateAPIView.as_view(), name='blog-list-create'),
    path('blogs/<int:pk>/', BlogDetailAPIView.as_view(), name='blog-detail'),
    path('blogs/search/', BlogSearchAPIView.as_view(), name='blog-search'),
    path('bookmark/', BookmarkAPIView.as_view(), name='bookmark'),
]
