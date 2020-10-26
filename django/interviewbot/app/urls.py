from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('restex/', test_rest),
    path('upload/', upload_view, name='upload'),
    path('videos/', video_preview, name='preview'),
    path('upload_video/', VideoUploadView.as_view()),
    path('next/', NextQuestionView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
