from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import permission_required

from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from app.serializers import *
from app.next_question import * 
from app.models import *
from app.form import *

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
			new_user = serializer.save() 
			request.session['is_reg'] = True
			request.session['user_id'] = new_user.id
			interview = Interview.objects.create(user=new_user)
			interview.save()
			request.session['interview_id'] = interview.id
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'OPTIONS':
		return Response(None, status=status.HTTP_204_NO_CONTENT)

class NextQuestionView(APIView):
	parser_classes = [MultiPartParser]
	permission_classes = ([])
	authentication_classes = ([])

	def get(self, request, *arg, **kwargs):
		dict = request.POST

		# Check se è prima domanda
		if 'type' in dict:
			if dict['type'] == 'base':
				first_question = Question.objects.get(pk=12)
				nq_serialized = QuestionSerializer(first_question)
				return Response(nq_serialized.data, status=status.HTTP_200_OK)
			else:
				print(dict, '##### PRIMO###############')
				return Response(status=status.HTTP_400_BAD_REQUEST)

		
		# check se sono presenti tutte le informazioni nella richiesta
		if not ('question_id' in dict and 'answer_text' in dict and 'answer_vid' in dict):
			print(dict, '##### SECONDO #############')
			return Response(status=status.HTTP_400_BAD_REQUEST)
		
		# estrazione dei dati dalla richiesta
		user_id 		= request.session['user_id']
		question_id 	= dict['question_id']
		interview_id 	= request.session['interview_id']
		answer_text 	= dict['answer_text']
		answer_vid 		= dict['answer_vid']

		user_obj = User.objects.get(pk=user_id)
		ans_question = Question.objects.get(pk=question_id)
		interview_obj = Interview.objects.get(pk=interview_id)

		if type(answer_vid) is str and ans_question.type != 'video':
			answer_vid = None
		elif type(answer_vid) is str or ans_question.type != 'video':
			return Response(status=status.HTTP_400_BAD_REQUEST)

		# Salvataggio della risposta nel database
		answer = Answer.objects.create(
			interview = interview_obj,
			user = user_obj,
			question = ans_question,
			choice_text = answer_text,
			choice_vid = answer_vid
		)
		answer.save()

		# Generazione prossima domanda
		
		next_question = self.get_next_question(id=question_id, answer=answer_text)

		if next_question is not None:
			if type(next_question) is int and next_question == 0:
				# Terminato, ritorna un messaggio adeguato e settare che il colloqui 
				# per quell'user è terminato e può essere analizzato dalle recruiter
				return Response(status=status.HTTP_202_ACCEPTED)
			else:
				nq_serialized = QuestionSerializer(next_question)
				if nq_serialized.is_valid():
					return Response(nq_serialized.data, status=status.HTTP_200_OK)
				else:
					return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)
		"""
		### Testing code ###
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
		
		"""

	def get_next_question(self, id, answer):

		# In questo metodo si deve far riferimento alla classe per l'elaborazione del
		# linguaggio naturale. Per ora le biforcazioni ci sono solamente per le domande
		# che presentano choices quindi non c'è una reale elaborazione del testo.

		question = Question.objects.get(id=id)
		if question is not None:
			flows = QuestionFlow.objects.all().filter(parent=question)
			if flows.exists() and flows.count() > 0:
				if flows.count() == 1:
					return flows.get(parent=question)
				elif not question.is_fork:
					return None
				else:
					if answer == "" or answer is None:
						return None
					for flow in flows:
						if flow.choice == answer:
							return flow
			else:
				return 0
		else:
			return None


@permission_required('app.can_add_question', raise_exception=True)
def add_question(request):
	### POST REQUEST ###
	if request.method == 'POST':
		if not ('type' in request.POST and 'action' in request.POST and 'length' in request.POST):
			return HttpResponse('Missing essentials parameters')
		
		type 		= request.POST['type']
		action 		= request.POST['action']
		length		= request.POST['length']

		if 'parent' in request.POST:
			parent 	= request.POST['parent']
		else:
			parent = None
		
		if 'choices' in request.POST:
			choices = request.POST['choices']
		else:
			choices = ""

		if 'is_fork' in request.POST:
			is_fork = True
		else:
			is_fork = False

		if 'choice_fork' in request.POST:
			choice_fork = request.POST['choice_fork']
		else:
			choice_fork = None
		
		question = Question.objects.create(type=type, action=action, length=length, choices=choices, is_fork=is_fork)
		question.save()

		if not (parent is None):
			parent_obj=Question.objects.get(pk=int(parent))
			flow = QuestionFlow.objects.create(parent=parent_obj, son=question, choice=choice_fork )
			flow.save()
		return HttpResponse('New question added with id: ' + str(question.id))
	
	### GET REQUEST ###
	elif request.method =='GET':
		question_list = []
		questions = Question.objects.all().order_by('-date_published')
		for question in questions:
			have_flow = QuestionFlow.objects.all().filter(parent=question).exists()
			if (not have_flow) or question.is_fork:
				question_list.append(question)
		
		choices_arr = []
		for question in question_list:
			if question.is_fork:
				choices = question.choices
				choices_arr += choices.split(';')

		return render(request, 'newquestion.html', {
			'questions': question_list,
			'choices': choices_arr,
		})


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
