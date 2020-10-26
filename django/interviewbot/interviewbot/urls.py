from django.contrib import admin
from django.urls import path, include
from app.models import *
from rest_framework import routers, serializers, viewsets

urlpatterns = [
    path('', include('app.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls'))
]
