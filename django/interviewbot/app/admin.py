from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Question)
admin.site.register(QuestionFlow)
admin.site.register(KeyWords)
admin.site.register(CandidateUser)
admin.site.register(Interview)

class QuestionAnswer(models.Answer):
    readonly_fields = ('date',)

admin.site.register(QuestionAnswer)