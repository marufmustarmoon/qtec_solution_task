from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from PIL import Image


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('normal', 'Normal User'),
        ('author', 'Author'),
    ]
    isAuthor = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name='customuser_set')
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set')




class Blog(models.Model):
    category = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=200, db_index=True)
    banner = models.ImageField(upload_to='blog_banners/')
    details = models.TextField()
    total_views = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    bookmarked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.banner:
            img = Image.open(self.banner.path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((800, 600))  # Adjust dimensions as needed
            img.save(self.banner.path)
        
        # Update search_vector
        self.search_vector = SearchVector('title', 'details')
        super().save(*args, **kwargs)

    @staticmethod
    def search(query):
        search_query = SearchQuery(query)
        # Filter blogs based on search query and rank results
        results = Blog.objects.annotate(rank=SearchRank(Blog.search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')
        return results
    

class Bookmark(models.Model):
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

