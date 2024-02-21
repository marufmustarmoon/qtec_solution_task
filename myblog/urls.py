from django.urls import include, path
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin-dj/', admin.site.urls),
    path('blog/', include('blog.urls')),
    path('silk/', include('silk.urls', namespace='silk')),
]
