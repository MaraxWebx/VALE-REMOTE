from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Question)
admin.site.register(QuestionFlow)
admin.site.register(KeyWords)
admin.site.register(CandidateUser)
admin.site.register(Interview)
admin.site.register(Answer)
admin.site.register(InterviewType)
admin.site.register(Comment)
admin.site.register(Token)