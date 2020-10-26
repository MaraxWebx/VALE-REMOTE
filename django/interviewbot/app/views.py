from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from app.models import *
from app.form import *
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from app.serializers import *
from app.next_question import * 

# Create your views here.
def upload_view(request):
	form = VideoModelForm()
	return render(request, 'upload_test.html', {'form':form})


def index(request):
	if request.session.get('is_reg', False):
		return render(request, 'index.html')
	else:
		request.session.flush()
		request.session.set_expiry(0)
		request.session['is_reg'] = False
		interview = Interview.objects.create()
		interview.save()
		request.session['interview_id'] = interview.id
		return render(request, 'credentials.html')

def video_preview(request):
	model = VideoModel.objects.all()
	return render(request, 'videos.html', {'query':model})

@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def test_rest(request):
	if request.method == 'POST':
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			print('New user')
			serializer.save() # <-- Da cambiare. Queste informazioni dovranno essere salvate più avanti.
			request.session['is_reg'] = True
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'OPTIONS':
		return Response(None, status=status.HTTP_204_NO_CONTENT)

class NextQuestionView(APIView):
	parser_classes = [MultiPartParser]
	permission_classes = ([])
	authentication_classes = ([])

	def get(self, request, *arg, **kwargs):
		dict = request.data

		# check se sono presenti tutte le informazioni nella richiesta
		if not ('id' in dict and 'question' in dict and 'interview_id' in dict and 'choice_text' in dict and 'choice_vid' in dict):
			return Response(status=status.HTTP_400_BAD_REQUEST)
		
		# estrazione dei dati dalla richiesta
		user_id 		= dict['id']
		question_id 	= dict['question']
		interview_id 	= request.session['interview_id']
		answer_text 	= dict['choice_text']
		answer_vid 		= dict['choice_vid']

		# Salvataggio della risposta nel database
		answer = Answer.objects.create(
			interview = interview_id,
			user = user_id,
			question = question_id,
			choice_text = answer_text,
			choice_vid = answer_vid
		)
		answer.save()

		# Di seguito è generata una domanda seguendo il modello presente in models.py
		# Non viene salvata nel database dato che è di prova.
		# Una futura implementazione implica che queste domande debbano essere prese dal database
		# con un certo criterio ed inviate al frontend. Qui invece viene sempre generata la stessa.
		
		next_question = Question.objects.create(
			type = "video",
			action = "Questa è la prossima domanda.",
			length = 0,
			choices = "",
		)

		# Serializzazione della domanda per inviarla tramite REST

		nq_serialized = QuestionSerializer(next_question)
		if nq_serialized.is_valid():
			return Response(nq_serialized.data, status=status.HTTP_200_OK)
		else:
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VideoUploadView(APIView):
	parser_classes = [MultiPartParser]
	permission_classes = ([])
	authentication_classes = ([])

	def post(self, request, *args, **kwargs):
		file = request.data.dict()['file']
		model = VideoModel.objects.create(video=file)
		model.save()
		return Response(status=status.HTTP_201_CREATED)

	def get(self, request, *args, **kwargs):
		form = VideoModelForm()
		return render(request, 'upload_test.html', {'form':form} )
