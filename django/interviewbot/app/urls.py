from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('restex/', test_rest),
    path('next/', NextQuestionView.as_view()),
    path('add_question/', add_question, name='add_question'),
    path('add_parent/', add_parent_to_join, name='add_parent'),
    path('interview/', interview, name='interview'),
    path('file/', test_file, name='test_file'),
    path('add_kw/', keyword_managment, name='add_keyword'),
    path('dashboard/', dashboard_index, name='dashboard'),
    path('login_rectruiter/', login_recruiter, name='login')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
