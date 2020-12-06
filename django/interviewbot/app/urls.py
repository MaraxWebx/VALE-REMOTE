from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('restex/', registration_view),
    path('next/', NextQuestionView.as_view()),
    path('interview/', interview, name='interview'),
    path('file/', test_file, name='test_file'),
    path('dashboard/', dashboard_index, name='dashboard'),
    path('dashboard/<int:id>', dashboard_interview, name='dashboard_interview'),
    path('dashboard/<int:id>/add_comment', dashboard_interview_addcomment, name='dashboard_interview_addcomment'),
    path('dashboard/<int:id>/mark', dashboard_interview_toggle_mark, name='dashboard_interview_togglemark'),
    path('dashboard/<int:id>/delete', dashboard_interview_delete, name='dashboard_interview_delete'),
    path('dashboard/interviews', dashboard_interview_type_list, name='dashboard_interview_list'),
    path('dashboard/interviews/<int:id>/keywords', dashboard_print_keywrods, name='dashboard_keywords_list'),
    path('dashboard/interviews/<int:id>/keywords/<int:id_kw>', dashboard_print_keywrod_flow, name='dashboard_keyword_flow_list'),
    path('dashboard/interviews/<int:id>', dashboard_print_interview, name='dashboard_print_interview'),
    path('dashboard/interviews/<int:id>/add_question', add_question, name='dashboard_add_question'),
    path('dashboard/interviews/<int:id>/edit', dashboard_edit_interviewtype, name='dashboard_edit_interview'),
    path('dashboard/interviews/<int:id>/delete', dashboard_delete_interviewtype, name='dashboard_delete_interview'),
    path('dashboard/interviews/<int:id>/edit/<int:q_id>', dashboard_question_edit, name='dashboard_edit_question'),
    path('dashboard/interviews/add_interview', add_interview, name='dashboard_add_interview'),
    path('dashboard/interviews/media/<path:name>', get_video_interview, name='get_video_interview'),
    path('dashboard/interviews/cv/<path:name>', get_cv_user, name='get_cv_user_interview'),
    path('login_recruiter/', login_recruiter, name='login'),
    path('logout/', logout_recruiter, name='logout'),
    path('keep_in_touch/', manutenzione, name='manutenzione')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
