from django.urls import include, path
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('admin-dj/', admin.site.urls),
    path('blog/', include('blog.urls')),
    path('silk/', include('silk.urls', namespace='silk')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
