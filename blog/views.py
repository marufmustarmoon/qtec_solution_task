
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
# from .serializers import UserRegistrationSerializer
from .serializers import UserLoginSerializer,BlogSerializer
from .utils import generate_access_token,verify_access_token_decorator
from .models import *
from fuzzywuzzy import process
from django.db.models import Q
from .serializers import BlogSerializer
from django.shortcuts import render
from .models import Blog
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Blog
from django.db import models
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.hashers import make_password
# from django.views.decorators.cache import cache_page
# from django.utils.decorators import method_decorator




class UserRegistrationAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        is_author = request.data.get('isAuthor', False)
        if User.objects.filter(username=username).exists():
            
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create(
            username=username,
            password=make_password(password),  
            isAuthor=is_author
        )
        
        return Response({"success": "User registered successfully"}, status=status.HTTP_201_CREATED)
    
    
    
class UserLoginAPIView(APIView):
    def post(self, request):
        print("moon")
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            try:
                user = User.objects.get(username=username)
                print(user)
            except User.DoesNotExist:
                user = None
            print(user.check_password(password))
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
        print(request.data)
        serializer = BlogSerializer(data=request.data,partial=True)
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
    # @method_decorator(cache_page(60 * 15))
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
            print(blog.total_views)
            blog.total_views += 1
            blog.save()

        except Blog.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BlogSerializer(blog)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookmarkAPIView(APIView):
    
    @verify_access_token_decorator
    def get(self, request, pk, *args, **kwargs):
        username = kwargs.get("username")
        print(username)
        try:
            blog = get_object_or_404(Blog, pk=pk)
            bookmark = get_object_or_404(Bookmark, user__username=username, blog=blog)
            print(bookmark)
            print(bookmark.bookmark)
            return Response({"bookmark": bookmark.bookmark}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Bookmark not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @verify_access_token_decorator
    def post(self, request, pk, *args, **kwargs):
        username = kwargs.get("username")
        user = User.objects.get(username=username)  # Obtain the user from the username
        try:
            blog = Blog.objects.get(pk=pk)
        except Blog.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
    
        bookmark, created = Bookmark.objects.get_or_create(user=user, blog=blog)  # Assign the user to the bookmark
        bookmark.bookmark = not bookmark.bookmark
        bookmark.save()
        print(bookmark.bookmark)
        return Response({"bookmark_status": bookmark.bookmark}, status=status.HTTP_200_OK)


    
    
    
class CheckisAuthorAPIView(APIView):
    @verify_access_token_decorator
    def get(self, request, *args, **kwargs):
        isAuthor = kwargs.get("isAuthor")
        username = kwargs.get("username")
        if isAuthor: 
            response_data = {   'isAuthor': True,'username':username }
            return Response(response_data, status=status.HTTP_200_OK)
        response_data = {'isAuthor': False,'username':username}
        return Response(response_data, status=status.HTTP_200_OK)
        
        
    
    
    



@staff_member_required
def dashboard(request):
    categories = Blog.objects.values('category').annotate(count=models.Count('category'))
    total_blogs = Blog.objects.count()
    category_data = [{'category': category['category'], 'percentage': (category['count'] / total_blogs) * 100} for category in categories]
    print(category_data)
    return render(request, 'admin/dashboard.html', {'category_data': category_data})

@staff_member_required
def blog_list(request):
    blogs = Blog.objects.all()
    categories = Blog.objects.values_list('category', flat=True).distinct()

    category_filter = request.GET.get('category')
    author_filter = request.GET.get('author')

    if category_filter:
        blogs = blogs.filter(category=category_filter)
    if author_filter:
        blogs = blogs.filter(author__username__icontains=author_filter)

    paginator = Paginator(blogs, 10)
    page_number = request.GET.get('page')
    blog_page = paginator.get_page(page_number)

    return render(request, 'admin/blog_list.html', {'blog_page': blog_page, 'categories': categories})