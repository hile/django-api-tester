
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('example/', include('apps.example.urls', namespace='example')),
    path('admin/', admin.site.urls),
]
