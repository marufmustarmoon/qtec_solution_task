
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
            serializer.save()
            return Response({'success': True, 'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None

            if user and user.check_password(password):
                isAuthor = user.isAuthor
                token = generate_access_token(username, isAuthor)
                return Response({'token': token}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class ProfileBlogListCreateAPIView(APIView):
    @verify_access_token_decorator
    def get(self, request, *args, **kwargs):
        isAuthor = kwargs.get("isAuthor")
        username = kwargs.get("username")
        if isAuthor: 
            blogs = Blog.objects.filter(author__username=username,author__isAuthor=isAuthor)
            serializer = BlogSerializer(blogs, many=True)
            response_data = {
                                'message': 'Blogs retrieved successfully',
                                'data': serializer.data
                            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        error_response_data = {
            'message': 'Error retrieving blogs',
            'errors': ['No blogs found']
        }
        return Response(error_response_data, status=status.HTTP_404_NOT_FOUND)

    @verify_access_token_decorator
    def post(self, request, *args, **kwargs):
        isAuthor = kwargs.get("isAuthor")
        username = kwargs.get("username")
        
        if not isAuthor:
            return Response(
                {"errors": [{"field": "auth", "message": "Only authors can create blogs"}]},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            author = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"errors": [{"field": "author", "message": "Author not found"}]},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=author)  # Save the author in the Blog model
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
        
        # user_type = kwargs.get("user_type")
        # if user_type == "author":
        #     username = kwargs.get("username")
        #     blogs = blogs.filter(author__username=username)

        serializer = BlogSerializer(blogs, many=True)
        response_data = {
            'message': 'Blogs retrieved successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    
class ProfileBlogDetailAPIView(APIView):
    @verify_access_token_decorator
    def get(self, request, pk, *args, **kwargs):
        try:
            username = kwargs.get("username")
            isAuthor = kwargs.get("isAuthor")
            if isAuthor:
                blog = Blog.objects.get(author__username=username, pk=pk)
            # else:
            #     blog = Blog.objects.get(pk=pk)

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
        
        
        isAuthor = kwargs.get("isAuthor")
        if isAuthor:
            
        
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
        
        
        isAuthor = kwargs.get("isAuthor")
        if isAuthor:
            blog.delete()
            return Response({"message": "Blog deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "You are not authorized to delete this blog"}, status=status.HTTP_403_FORBIDDEN)



    
    
class BlogListCreateAPIView(APIView):
    @verify_access_token_decorator
    def get(self, request, *args, **kwargs):
        
        blogs = Blog.objects.all()
        if blogs:
            serializer = BlogSerializer(blogs, many=True)
            response_data = {
                                'message': 'Blogs retrieved successfully',
                                'data': serializer.data
                            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        error_response_data = {
            'message': 'Error retrieving blogs',
            'errors': ['No blogs found']
        }
        return Response(error_response_data, status=status.HTTP_404_NOT_FOUND)
    
class BlogDetailAPIView(APIView):
    @verify_access_token_decorator
    def get(self, request, pk, *args, **kwargs):
        try:
            
            blog = Blog.objects.get(pk=pk)

        except Blog.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BlogSerializer(blog)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookmarkAPIView(APIView):
    @verify_access_token_decorator
    def post(self, request, *args, **kwargs):
        username = kwargs.get("username")
        blog_id = request.data.get('blog_id')
        try:
            blog = Blog.objects.get(pk=blog_id)
        except Blog.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
        
        bookmark, created = Bookmark.objects.get_or_create(user__username=username, blog=blog)
        if created:
            return Response({"message": "Blog bookmarked successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Blog already bookmarked"}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        username = kwargs.get("username")
        blog_id = request.data.get('blog_id')
        try:
            bookmark = Bookmark.objects.get(user__username=username, blog_id=blog_id)
        except Bookmark.DoesNotExist:
            return Response({"error": "Bookmark not found"}, status=status.HTTP_404_NOT_FOUND)
        
        bookmark.delete()
        return Response({"message": "Bookmark removed successfully"}, status=status.HTTP_204_NO_CONTENT)