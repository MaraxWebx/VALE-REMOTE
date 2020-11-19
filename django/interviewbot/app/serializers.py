from app.models import *
from rest_framework import serializers

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id','type','action','length','choices']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateUser
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'
