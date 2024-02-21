from django.contrib import admin
from .models import User, Blog
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from django.core.paginator import Paginator
from django.db.models import Q
from .views import blog_dashboard

# # Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    list_filter = ('username',)
    search_fields = ('username', 'email')

# # @admin.register(Blog)
# # class BlogAdmin(admin.ModelAdmin):
# #     list_display = ('title', 'category', 'author', 'total_views', 'created_at')
# #     list_filter = ('category', 'author')
# #     search_fields = ('title', 'category', 'author__username')
# #     readonly_fields = ('total_views', 'created_at', 'updated_at')
    




@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'total_views', 'created_at')
    list_filter = ('category', 'author')
    search_fields = ('title', 'category', 'author__username')
    readonly_fields = ('total_views', 'created_at', 'updated_at')
    
    def get_urls(self):
        urls = super().get_urls()
        print(urls)
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(blog_dashboard), name='blog-dashboard'),
            # path('list/', self.admin_site.admin_view(blog_list), name='blog-list'),
        ]
        print(custom_urls + urls)
        return custom_urls + urls

