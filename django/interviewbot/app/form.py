from django import forms
from .models import *

class VideoModelForm(forms.ModelForm):
	class Meta:
		model = VideoModel
		fields = ('video',)