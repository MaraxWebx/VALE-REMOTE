from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.utils.safestring import mark_safe

from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser, JSONParser
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes

from app.serializers import *
from app.next_question import * 
from app.graph import *
from app.models import *
from app.form import *
from app.text_analyzer import TextAnalyzer
from app.text_filter import Filter
from app.text_sentiment import SentimentAnalyzer

SA = SentimentAnalyzer()


"""
bow_path = "/var/www/site/bow.json"
controller = Controller()
"""

# Create your views here.
def index(request):
	if request.session.get('is_reg', False):
		
		return redirect('/interview/')
	else:
		request.session.clear_expired()
		request.session.flush()
		request.session.set_expiry(300)
		request.session['is_reg'] = False
		return render(request, 'credentials.html')

def interview(request):
	if  request.session.get('is_reg', False):
		return render(request,'index.html')
	else:
		return redirect('/')

@api_view(['POST'])
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

class NextQuestionView(APIView):
	parser_classes = [MultiPartParser]
	permission_classes = ([])
	authentication_classes = ([])

	def get(self, request, *arg, **kwargs):
		dict = request.query_params
		request.session['refresh'] = True
		# Check se è prima domanda
		if 'type' in dict:
			if dict['type'] == 'base':
				first_question = Question.objects.get(pk=12)
				nq_serialized = QuestionSerializer(first_question)
				return Response(nq_serialized.data, status=status.HTTP_200_OK)
			else:
				return Response(status=status.HTTP_400_BAD_REQUEST)

		# check se sono presenti tutte le informazioni nella richiesta
		if not ('question_id' in dict and 'answer_text' in dict):
			return Response(status=status.HTTP_400_BAD_REQUEST)
		
		# estrazione dei dati dalla richiesta
		user_id 		= request.session['user_id']
		question_id 	= dict['question_id']
		interview_id 	= request.session['interview_id']
		answer_text 	= dict['answer_text']
		
		user_obj = User.objects.get(pk=user_id)
		ans_question = Question.objects.get(pk=question_id)
		interview_obj = Interview.objects.get(pk=interview_id)

		# Salvataggio della risposta nel database
		answer = Answer.objects.create(
			interview = interview_obj,
			user = user_obj,
			question = ans_question,
			choice_text = answer_text,
			choice_vid = None
		)
		answer.save()

		if dict['answer_vid'] == 'to_upload':
			request.session['last_ans_id'] = answer.id
		else:
			request.session['last_ans_id'] = -1

		# Generazione prossima domanda
		next_question = self.get_next_question(id=question_id, answer=answer_text)

		if next_question is not None:
			if type(next_question) is int and next_question == 0:
				# Terminato, ritorna un messaggio adeguato e settare che il colloqui 
				# per quell'user è terminato e può essere analizzato dalle recruiter
				return Response(status=status.HTTP_202_ACCEPTED)
			else:
				nq_serialized = QuestionSerializer(next_question)
				return Response(nq_serialized.data, status=status.HTTP_200_OK)
		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)
	
	def post(self, request, *arg, **kwargs):
		file = request.data.dict()['file']
		request.session['refresh'] = True
		if request.session.get('last_ans_id', -1) > 0:
			last_ans = Answer.objects.get(pk=request.session['last_ans_id'])
			request.session['last_ans_id'] = -1
			last_ans.choice_vid = file
			last_ans.save()
			return Response(status=status.HTTP_201_CREATED)
		else:
			print(" ## ERR ## - User session doesn't have a last_ans_id setted. Cannot save the video.")
			return Response(status=status.HTTP_400_BAD_REQUEST)

	def get_next_question(self, id, answer):

		# In questo metodo si deve far riferimento alla classe per l'elaborazione del
		# linguaggio naturale. Per ora le biforcazioni ci sono solamente per le domande
		# che presentano choices quindi non c'è una reale elaborazione del testo.

		question = Question.objects.get(id=id)
		if question is not None:
			if question.type == 'check' or question.type == 'code':
				flows = QuestionFlow.objects.all().filter(parent=question)
				if flows.exists() and flows.count() > 0:
					if flows.count() == 1:
						return flows.get(parent=question).son
					elif not question.is_fork:
						return None
					else:
						if answer == "" or answer is None:
							return None
						for flow in flows:
							if flow.choice == answer:
								return flow.son
				else:
					return 0
			else:
				analyzer = TextAnalyzer(answer)
				analyze_results = analyzer.analyze()

				filter = Filter()
				filter_results = filter.execute(analyze_results)
				
				# Controllare che filter non sia vuoto

				sentiment = SA.execute(filter_results)

				key_max = ""
				value_max = -999999999

				for key in sentiment:
					if sentiment[key] > value_max:
						value_max = sentiment[key]
						key_max = key

				# controllare la soglia minima

				print('############ finding : ', key_max)
				kw_question = KeyWords.objects.filter(word=key_max)[0]
				return kw_question.start_question

		else:
			return None

@api_view(['POST'])
@parser_classes([MultiPartParser])
def test_file(request):
	file = request.data['file']

	if not file.name.endswith('.pdf'):
		id = request.session.get('user_id', -1)
		if id > 0:
			user = User.objects.get(pk=id)
			user.delete()
		request.session['is_reg'] = False
		return Response(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
	
	id = request.session.get('user_id', -1)
	if id < 0:
		return Response(status=status.HTTP_400_BAD_REQUEST)

	user = User.objects.get(pk=id)
	user.cv = file
	user.save()
	return Response(status=status.HTTP_201_CREATED)

@api_view(['POST','GET'])
@permission_required('app.can_add_question', raise_exception=True)
def keyword_managment(request):
	if request.method == 'GET':
		request.session['what'] = -1
		return render(request, 'new_keyword.html', context = {'esito':''})

	elif request.method == 'POST':
			if request.session.get('what', -1) < 0:  #new word
				request.session['what'] = 1
				if 'word' in request.POST and 'n' in request.POST:
					word = request.POST['word']
					request.session['word'] = word
					request.session['n'] = request.POST['n']
					n = request.session['n']
					return render(request, 'new_kw_question.html', context={'num':n})
					#INIZIA INSERIMENTO DOMANDE
				else:
					#MISSING PARAMETERS
					return HttpResponse('Missing essentials parameters')

			else:										#new questionflow
				if request.session.get('word', False) and request.session.get('n', False):
					n = int(request.session['n'])
					if n > 0:
						tmp_parent = request.session.get('last_id', None)
						if not ('type' in request.POST and 'action' in request.POST and 'length' in request.POST):
							return HttpResponse('Missing essentials parameters')
						
						type 		= request.POST['type']
						action 		= request.POST['action']
						length		= request.POST['length']
						if 'choices' in request.POST:
							choices = request.POST['choices']
							if choices.endswith(';'):
								choices = choices[:-1]
						else:
							choices = ""
						
						new_quest = Question.objects.create(type=type, action=action, length=length, choices=choices)
						new_quest.save()

						if tmp_parent is not None:
							parent = Question.objects.get(pk=int(tmp_parent))
							flow = QuestionFlow.objects.create(parent=parent, son = new_quest)
							flow.save()
						else:
							word = request.session['word']
							kw = KeyWords.objects.create(word=word, start_question=new_quest)
							kw.save()
						
						request.session['last_id'] = new_quest.id
						request.session['n'] = n - 1
						if n - 1 <= 0:
							request.session['what'] = -1
							return render(request, 'new_keyword.html', context = {'esito':"Keyword aggiunta con successo."})
							# MOSTRA FINE
						else:
							return render(request, 'new_kw_question.html', context={'num':n})
							# PROSSIMA DOMANDA

					else:
						request.session['what'] = -1
						return HttpResponse("Numero di domande non valido.")
					return render(request, 'new_kw_question.html', context={'num':n})
				else:
					return HttpResponse("Numero parametri errato")

	return Response(status=status.HTTP_400_BAD_REQUEST)

		



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
			if choices.endswith(';'):
				choices = choices[:-1]
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
		
		new_question = Question.objects.create(type=type, action=action, length=length, choices=choices, is_fork=is_fork)
		new_question.save()

		if not (parent is None):
			parent_obj=Question.objects.get(pk=int(parent))
			flow = QuestionFlow.objects.create(parent=parent_obj, son=new_question, choice=choice_fork )
			flow.save()

		if 'is_join' in request.POST:
			return redirect('/add_parent/?n=' + str(request.POST['is_join']) + '&id=' + str(new_question.id))

		return HttpResponse('New question added with id: ' + str(new_question.id))
	
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
			'esito': ""
		})

@permission_required('app.can_add_question', raise_exception=True)
def add_parent_to_join(request):
	if request.method == 'POST':
		
		son_obj = Question.objects.get(pk=request.session['join_id'])

		n = int(request.session['parent_num'])
		for i in range(n):
			if str(i) not in request.POST:
				break
			else:
				parent_id = request.POST[str(i)]
				parent_obj = Question.objects.get(pk=parent_id)
				flow = QuestionFlow.objects.create(parent=parent_obj, son=son_obj, choice="")
				flow.save()
		# response = HttpResponse("New question created with id: " + str(request.session['join_id']))
		request.session['parent_num'] = -1
		request.session['join_id'] = -1
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
			'esito': "Domanda aggiunta con successo."
		})

	elif request.method == 'GET':
		n = request.GET['n']
		question_id = request.GET['id']
		request.session['parent_num'] = n
		request.session['join_id'] = question_id

		question_list = []
		questions = Question.objects.all().order_by('-date_published')
		new_question = Question.objects.get(pk=int(question_id))
		for question in questions:
			if question is new_question:
				continue
			have_flow = QuestionFlow.objects.all().filter(parent=question).exists()
			if (not have_flow) or question.is_fork:
				question_list.append(question)
		return render(request, 'addparent.html', context={
			'parent_number': range(int(n)),
			'questions': question_list
		})
		
@permission_required('app.can_add_question', raise_exception=True)
def question_graph(request):
	if request.method == 'GET':
		graph = QuestionGraph()
		questionflow = QuestionFlow.objects.all()
		for flow in questionflow:
			graph.add_edge(flow.parent, flow.son, choice=flow.choice)
		
		html = '<h1>List of all possible path</h1><br/><ul>'
		for key in graph.get_vertices():
			vert = graph.get_vertex(key)
			if not vert.seen_as_child:
				html += DFS(vert)
		html += '</ul>'
		return render(request, 'graph.html',context={'graph': mark_safe(html)})

def DFS(v):
	v.seen = True
	ret = '<li>--' + v.get_choice() + '-->' + v.question.action + '</li>'

	if not v.adjacent:
		return ret
	else:
		ret = '<li>--' + v.get_choice() + '-->'+ v.question.action + '</li>'
		ret += '<ul>'
	for x in v.adjacent:
		v.adjacent[x].seen_as_child = True
		ret += DFS(v.adjacent[x])

	ret += '</ul>'
	return ret


