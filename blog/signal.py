# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from django.core.cache import cache
# from .models import Bookmark

# BLOG_LIST_CACHE_KEY = 'blog_list_cache_key'

# @receiver(post_save, sender=Bookmark)
# def bookmark_post_save(sender, instance, **kwargs):
#     cache.delete(BLOG_LIST_CACHE_KEY)

# @receiver(post_delete, sender=Bookmark)
# def bookmark_post_delete(sender, instance, **kwargs):
#     cache.delete(BLOG_LIST_CACHE_KEY)
