from django.urls import path
from .views import UserLoginAPIView,ProfileBlogListCreateAPIView,UserRegistrationAPIView,BlogSearchAPIView,ProfileBlogDetailAPIView,BookmarkAPIView,BlogListCreateAPIView,BlogDetailAPIView


urlpatterns = [
    path('api/register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('api/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('profile/blogs/', ProfileBlogListCreateAPIView.as_view(), name='blog-list-create'),
    path('profile/blogs/<int:pk>/', ProfileBlogDetailAPIView.as_view(), name='blog-detail'),
    path('blogs/search/', BlogSearchAPIView.as_view(), name='blog-search'),
    path('blogs/', BlogListCreateAPIView.as_view(), name='blog-list-create'),
    path('blogs/<int:pk>/', BlogDetailAPIView.as_view(), name='blog-detail'),
    path('bookmark/', BookmarkAPIView.as_view(), name='bookmark'),
]
