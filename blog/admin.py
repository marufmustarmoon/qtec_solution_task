from django.contrib import admin
from .models import User, Blog,Bookmark
from django.contrib import admin


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
    

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'bookmark', 'created_at')
    list_filter = ('user', 'bookmark')
    search_fields = ('user__username', 'blog__title')