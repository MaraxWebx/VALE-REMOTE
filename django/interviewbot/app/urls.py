from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('restex/', test_rest),
    path('next/', NextQuestionView.as_view()),
    # path('add_question/', add_question, name='add_question'),
    path('add_parent/', add_parent_to_join, name='add_parent'),
    path('interview/', interview, name='interview'),
    path('file/', test_file, name='test_file'),
    path('add_kw/', keyword_managment, name='add_keyword'),
    path('dashboard/', dashboard_index, name='dashboard'),
    path('dashboard/<int:id>', dashboard_interview, name='dashboard_interview'),
    path('dashboard/<int:id>/add_comment', dashboard_interview_addcomment, name='dashboard_interview_addcomment'),
    path('dashboard/<int:id>/mark', dashboard_interview_toggle_mark, name='dashboard_interview_togglemark'),
    path('dashboard/questions', dashboard_interview_list, name='dashboard_interview_list'),
    path('dashboard/add_question', add_question, name='dashboard_add_question'),
    path('dashboard/questions/<int:id>', dashboard_print_interview, name='dashboard_print_interview'),
    path('login_rectruiter/', login_recruiter, name='login'),
    path('logout/', logout_recruiter, name='logout')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
