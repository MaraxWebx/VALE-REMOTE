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
    path('graph/', question_graph, name='graph')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
