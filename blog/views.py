
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer
from .serializers import UserLoginSerializer,BlogSerializer
from .utils import generate_access_token,verify_access_token_decorator
from .models import *
from fuzzywuzzy import process
from django.db.models import Q
from .serializers import BlogSerializer

class UserRegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            User.objects.create(username=request.data['username'], password=request.data['password'],user_type=request.data['user_type'])

            return Response({'success': True, 'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user_type = serializer.validated_data['user_type']

            try:
                user = User.objects.get(username=username, user_type=user_type)
            except User.DoesNotExist:
                user = None
                
            if user:
                token = generate_access_token(username,user_type)
                return Response({'token': token}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class BlogListCreateAPIView(APIView):
    @verify_access_token_decorator
    def get(self, request, *args, **kwargs):
        user_type = kwargs.get("user_type")
        username = kwargs.get("username")
        if user_type == "author":

            
            blogs = Blog.objects.filter(author__username=username,author__user_type=user_type)
            
        elif user_type == "normal":
            blogs = Blog.objects.all()
        else:
            return Response(
                {"errors": [{"field": "auth", "message": "Invalid user type"}]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = BlogSerializer(blogs, many=True)
        response_data = {
                            'message': 'Blogs retrieved successfully',
                            'data': serializer.data
                        }
        return Response(response_data, status=status.HTTP_200_OK)

    @verify_access_token_decorator
    def post(self, request, *args, **kwargs):
        user_type = kwargs.get("user_type")
        if user_type != "author":
            return Response(
                {"errors": [{"field": "auth", "message": "Only authors can create blogs"}]},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BlogSearchAPIView(APIView):
    @verify_access_token_decorator
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')

        if not query:
            return Response(
                {"errors": [{"field": "query", "message": "Search query is required"}]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        
        corrected_query, score = process.extractOne(query, Blog.objects.values_list('title', flat=True))
        
       
        blogs = Blog.objects.filter(title__icontains=corrected_query)
        
        user_type = kwargs.get("user_type")
        if user_type == "author":
            username = kwargs.get("username")
            blogs = blogs.filter(author__username=username)

        serializer = BlogSerializer(blogs, many=True)
        response_data = {
            'message': 'Blogs retrieved successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    
class BlogDetailAPIView(APIView):
    @verify_access_token_decorator
    def get(self, request, pk, *args, **kwargs):
        try:
            username = kwargs.get("username")
            user_type = kwargs.get("user_type")
            if user_type == "author":
                blog = Blog.objects.get(author__username=username, pk=pk)
            else:
                blog = Blog.objects.get(pk=pk)

        except Blog.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BlogSerializer(blog)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @verify_access_token_decorator
    def patch(self, request, pk, *args, **kwargs):
        try:
            username = kwargs.get("username")
            blog = Blog.objects.get(author__username=username,pk=pk)
        except Blog.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
        user_type = kwargs.get("user_type")
        if user_type == "author":
            
        
            serializer = BlogSerializer(blog, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({"error": "You are not authorized to update this blog"}, status=status.HTTP_403_FORBIDDEN)
        
        

    @verify_access_token_decorator
    def delete(self, request, pk, *args, **kwargs):
        try:
            username = kwargs.get("username")
            blog = Blog.objects.get(author__username=username,pk=pk)
        except Blog.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
        user_type = kwargs.get("user_type")
        if user_type == "author":
            blog.delete()
            return Response({"message": "Blog deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "You are not authorized to delete this blog"}, status=status.HTTP_403_FORBIDDEN)


class BookmarkAPIView(APIView):
    @verify_access_token_decorator
    def post(self, request, *args, **kwargs):
        username = kwargs.get("username")
        blog_id = request.data.get('blog_id')
        
        try:
            blog = Blog.objects.get(pk=blog_id, author__username=username)
        except Blog.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Update the 'bookmarked' field to True
        blog.bookmarked = True
        blog.save()
        
        return Response({"message": "Blog bookmarked successfully"}, status=status.HTTP_201_CREATED)

    @verify_access_token_decorator
    def delete(self, request, *args, **kwargs):
        username = kwargs.get("username")
        blog_id = request.data.get('blog_id')
        
        try:
            blog = Blog.objects.get(pk=blog_id, author__username=username)
        except Blog.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Update the 'bookmarked' field to False
        blog.bookmarked = False
        blog.save()
        
        return Response({"message": "Bookmark removed successfully"}, status=status.HTTP_204_NO_CONTENT)