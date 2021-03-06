from django.db import models
from django import forms
import datetime

# Create your models here.

class Question(models.Model):
	type = models.CharField(max_length=15, default="", null=True, blank=True)
	action = models.CharField(max_length=1500)
	length = models.IntegerField(default=0)
	choices = models.CharField(max_length=500, default="", null=True, blank=True)
	is_fork = models.BooleanField(default=False)
	date_published = models.DateTimeField('date published', auto_now_add=True)
	to_analyze = models.BooleanField(default=False)
	is_technical = models.BooleanField(default=False)
	addedby = models.CharField(max_length=100, default="Anymous")
	id_interview_type = models.IntegerField(default=1)

class QuestionFlow(models.Model):
	parent = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='parent')
	son = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question')
	choice = models.CharField(max_length=100, default="", null=True, blank=True)

class CandidateUser(models.Model):
	firstname = models.CharField(max_length=50)
	lastname = models.CharField(max_length=50)
	email = models.CharField(max_length=100)
	cv = models.FileField(upload_to='user_cvs/', null = True)

	def __str__(self):
		return self.firstname + ' ' + self.lastname

class InterviewType(models.Model):
	interview_name = models.CharField(max_length=200, null = False, blank=False)
	start_question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True)
	addedby = models.CharField(max_length=100, default = "Human Resource")
	date_published = models.DateTimeField('date published', auto_now_add=True)

class Interview(models.Model):
	date = models.DateTimeField('date published', auto_now_add=True)
	user = models.ForeignKey(CandidateUser, on_delete=models.CASCADE)
	analyzed = models.BooleanField(default=False)
	type = models.ForeignKey(InterviewType, on_delete=models.CASCADE)

class MatchKeyword(models.Model):
	word = models.CharField(max_length=100, null=False, blank=False)
	rating = models.FloatField(null=False, blank=False)
	interview = models.ForeignKey(Interview, on_delete=models.CASCADE)

class Comment(models.Model):
	interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
	content = models.CharField(max_length=500, null = False, blank = False)
	author = models.CharField(max_length=100, null = False, blank = False)

class Answer(models.Model):
	interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
	user = models.ForeignKey(CandidateUser, on_delete=models.CASCADE)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	choice_text = models.CharField(max_length=500, null=True)
	choice_vid = models.FileField(upload_to='videos/', null=True,)
	registered = models.DateTimeField('date published', auto_now_add=True)

	def __str__(self):
		return self.user.firstname + ' ' + self.user.lastname + ' ' + self.question.type + ' (' + str(self.id) + ')'

class KeyWords(models.Model):
	word = models.CharField(max_length=100, null=False, blank=False)
	start_question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
	interviewtype = models.ForeignKey(InterviewType, on_delete=models.CASCADE)

	def __str__(self):
		return self.word + ' (' + str(self.id) + ')'

class Token(models.Model):
	token = models.CharField(max_length=15, null=False, blank=False)
	interview = models.ForeignKey(InterviewType, on_delete=models.CASCADE)
	generated_by = models.CharField(max_length=50, default="Anonymous", blank=False, null=False)
	generated_date = models.DateTimeField('date generated', auto_now_add=True)
	usages = models.IntegerField(default=-1)

	def __str__(self):
		return '(' + self.id + ') Token for ' + self.interview.interview_name


class DefaultInterview(models.Model):
	default_interview = models.ForeignKey(InterviewType, on_delete=models.CASCADE)
	last_modify = models.DateTimeField('last modify', auto_now_add=True)
	modify_by = models.CharField(max_length=50, default="Anonymous", blank=False, null=False)

	def __str__(self):
		return str(self.id) + ') Default: ' + self.default_interview.interview_name