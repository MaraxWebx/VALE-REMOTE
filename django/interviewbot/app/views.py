from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, FileResponse
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
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
from app.utils import get_next_question, get_next_question_v2, logger
from app.text_analyzer import TextAnalyzer
from app.text_filter import Filter
from app.text_sentiment import SentimentAnalyzer

SA = SentimentAnalyzer()

SITO_IN_MANUTENZIONE = False

def manutenzione(request):
	return render(request, 'manutenzione.html')

def test_check_user_group(user):
	return user.groups.filter(name='recruiter').exists() or user.is_superuser


def index(request):
	if SITO_IN_MANUTENZIONE and not test_check_user_group(request.user):
		return redirect('/keep_in_touch/')
	if request.method == 'GET':
		if request.session.get('is_reg', False):
			logger('Access index but already registred, redirected', session=request.session)
			return redirect('/interview/')
		else:
			request.session.clear_expired()
			request.session.set_expiry(300)
			request.session['is_reg'] = False
			interviewtype_id = request.GET.get('interview', -1)

			if int(interviewtype_id) > 0:
				logger('Access index with a custom interview', session=request.session)
				interviewtype = InterviewType.objects.filter( pk = int(interviewtype_id))
				if interviewtype.exists() and interviewtype.count() == 1:
					request.session['interview'] = interviewtype_id
				else:
					request.session['interview'] = -1
					logger('Custom interview is not valid', session=request.session)
			else:
				logger('Access index with no custom interview', session=request.session)

			return render(request, 'credentials.html')

def interview(request):
	if SITO_IN_MANUTENZIONE and not test_check_user_group(request.user):
		return redirect('/keep_in_touch/')
	if  request.session.get('is_reg', False) and CandidateUser.objects.filter(pk=request.session.get('user_id', -1)).count() > 0:
		logger('Starting new interview', session=request.session)
		return render(request,'index.html')
	else:
		logger('Access interview but not registered yet', session=request.session)
		request.session['is_reg'] = False
		request.session['user_id'] = -1
		return redirect('/')

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def registration_view(request):
	if request.method == 'POST':
		try:
			serializer = UserSerializer(data=request.data)
			if serializer.is_valid():
				new_user = serializer.save() 
				request.session['is_reg'] = True
				request.session['user_id'] = new_user.id
				if request.session.get('interview', -1) < 0:
					request.session['interview'] = 2
				type = InterviewType.objects.get(pk = int(request.session.get('interview', 2)))
				interview = Interview.objects.create(user=new_user, type = type)
				interview.save()
				request.session['interview_id'] = interview.id
				logger('New user registered', session=request.session)
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			logger('Try to add new user with invalid data.', session=request.session)
			return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			logger('Exeption occurred in restex', session=request.session)
			print(e)
			return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	return Response(status=status.HTTP_200_OK)

class NextQuestionView(APIView):
	parser_classes = [MultiPartParser]
	permission_classes = ([])
	authentication_classes = ([])

	def get(self, request, *arg, **kwargs):
		dict = request.query_params
		request.session['refresh'] = True

		# Check se è prima domanda

		""" # Old one # 
		if 'type' in dict:
			if dict['type'] == 'base':
				if int(request.session.get('interview', -1 )) > 0:
					interviewtype = InterviewType.objects.filter(pk = int(request.session['interview']))
					if interviewtype.exists() and interviewtype.count() == 1:
						first_question = interviewtype[0].start_question
						nq_serialized = QuestionSerializer(first_question)
						return Response(nq_serialized.data, status=status.HTTP_200_OK)
				first_question = Question.objects.get(pk=77)
				nq_serialized = QuestionSerializer(first_question)
				return Response(nq_serialized.data, status=status.HTTP_200_OK)
			else:
				return Response(status=status.HTTP_400_BAD_REQUEST)

		"""

		if 'type' in dict:
			if dict['type'] == 'base':
				logger('Request base question', session=request.session)
				if int(request.session.get('interview', -1)) > 0:
					logger('Interview already setted', session=request.session)
					interviewtype = InterviewType.objects.filter(pk = int(request.session['interview']))
					if interviewtype.exists() and interviewtype.count() == 1:
						if request.session.get('last_ans_question', -1) > 0:
							id = int(request.session['last_ans_question'])
							if id > 0:
								logger('Resume interview at question with id ' + str(id), session = request.session)
								question = Question.objects.get(pk=id)
								q_serialized = QuestionSerializer(question)
								return Response(q_serialized.data, status = status.HTTP_200_OK)
						else:
							logger('Starting new interview', session = request.session)
							first_question = interviewtype[0].start_question
							nq_serialized = QuestionSerializer(first_question)
							return Response(nq_serialized.data, status = status.HTTP_200_OK)
				else: #get the default
					default = DefaultInterview.objects.all()[0]
					request.session['interview'] = default.default_interview.id
					logger('Interview not setted, getting default: ' + request.session['interview'], session=request.session)
					question = default.default_interview.start_question
					d_serialized = QuestionSerializer(question)
					return Response(d_serialized.data, status=status.HTTP_200_OK)
			else:
				logger('Invalid request in Type', request.session)
				return Response(status=status.HTTP_400_BAD_REQUEST)
				

		# check se sono presenti tutte le informazioni nella richiesta
		if not ('question_id' in dict):
			return Response(status=status.HTTP_400_BAD_REQUEST)

		
		# estrazione dei dati dalla richiesta
		user_id 		= request.session['user_id']
		question_id 	= dict['question_id']
		interview_id 	= request.session['interview_id']
		if 'answer_text' in dict:
			answer_text = dict['answer_text']
		else:
			answer_text = ""

		user_obj = CandidateUser.objects.get(pk=user_id)
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

		logger('New answer with id: ' + str(answer.id) + ' to the question: ' + str(question_id) + ' type: ' + str(ans_question.type), session=request.session)

		if dict['answer_vid'] == 'to_upload':
			request.session['last_ans_id'] = answer.id
			logger('Waiting for the vid to be setted...', session=request.session)

		# Generazione prossima domanda

		next_question = get_next_question_v2(SA, question_id, answer_text, request.session)

		if next_question is not None:
			if type(next_question) is int and next_question == 0:
				request.session['is_reg'] = False
				
				return Response(status = status.HTTP_202_ACCEPTED)
			request.session['last_ans_question'] = int(next_question.id)
			nq_serialized = QuestionSerializer(next_question)
			return Response(nq_serialized.data, status=status.HTTP_200_OK)
		return Response(status=status.HTTP_400_BAD_REQUEST)

		""" # IMPL per get_next_question() # 
		if next_question is not None:
			if type(next_question) is int and next_question == 0:
				if int(request.session.get('last_base_quest', - 1)) > 0:
					question = Question.objects.get(id=request.session['last_base_quest'])
					request.session['last_base_quest'] = -1
					request.session['have_forked'] = False
					flows = QuestionFlow.objects.all().filter(parent=question)
					if flows.exists() and flows.count() == 1:
						next_question = flows.get(parent=question).son
					elif flows.count() > 0:
						for flow in flows:
							if not flow.son.is_technical:
								next_question = flow.son
					else:
						return Response(status=status.HTTP_202_ACCEPTED)
				else:
					return Response(status=status.HTTP_202_ACCEPTED)
			
			nq_serialized = QuestionSerializer(next_question)
			return Response(nq_serialized.data, status=status.HTTP_200_OK)
		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)
		"""


	def post(self, request, *arg, **kwargs):
		file = request.data.dict()['file']
		request.session['refresh'] = True
		logger('New post request on next', session=request.session)
		if request.session.get('last_ans_id', -1) > 0:
			logger('Valid last_ans_id setted, referencing the video', session=request.session)
			last_ans = Answer.objects.get(pk=request.session['last_ans_id'])
			request.session['last_ans_id'] = -1
			last_ans.choice_vid = file
			last_ans.save()
			return Response(status=status.HTTP_201_CREATED)
		else:
			logger('Cannot reference this file, no last_ans_id setted.', session=request.session)
			return Response(status=status.HTTP_400_BAD_REQUEST)

	

@api_view(['POST'])
@authentication_classes([])
@parser_classes([MultiPartParser])
def test_file(request):
	file = request.data['file']

	if not file.name.endswith('.pdf'):
		id = request.session.get('user_id', -1)
		if id > 0:
			user = CandidateUser.objects.get(pk=id)
			user.delete()
		request.session['is_reg'] = False
		return Response(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
	
	id = request.session.get('user_id', -1)
	if id < 0:
		return Response(status=status.HTTP_400_BAD_REQUEST)

	user = CandidateUser.objects.get(pk=id)
	user.cv = file
	user.save()
	return Response(status=status.HTTP_201_CREATED)

@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def add_interview(request):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')

	if request.method=='GET':
		return render(request, 'add-interview.html')
	elif request.method=='POST':
		if not 'action' in request.POST:
			return HttpResponse('Missing interview name')
		name = request.POST['action']
		new_interview_type = InterviewType.objects.create(interview_name = name, addedby=(str(request.user.first_name) + ' ' + str(request.user.last_name)))
		new_interview_type.save()
		return redirect('/dashboard/interviews')

@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def add_question(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')
	if not InterviewType.objects.all().filter(pk=id).exists():
		return redirect('/dashboard/interviews')

	### POST REQUEST ###
	if request.method == 'POST':
		if not ('type' in request.POST and 'action' in request.POST ):
			return HttpResponse('Missing essentials parameters')
		
		type 		= request.POST['type']
		action 		= request.POST['action']

		if 'length' in request.POST:
			length	= request.POST['length']
		if 'lang' in request.POST:
			lang = request.POST['lang']
		if type == 'code':
			length = lang
			
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

		analyze = False
		if type == 'video':
			if 'ai' in request.POST:
				analyze = request.POST['ai']
		
		new_question = Question.objects.create(type=type, action=action, length=length, choices=choices, is_fork=is_fork, id_interview_type=int(id), to_analyze=analyze)
		new_question.save()

		if 'check_parent' in request.POST:
			parents = request.POST.getlist('check_parent')
			for parent_id in parents:
				parent = Question.objects.get(pk=int(parent_id))
				flow = QuestionFlow.objects.create(parent=parent, son=new_question, choice=choice_fork )
				flow.save()

		interview = InterviewType.objects.get(pk=int(id))
		if not interview.start_question:
			interview.start_question = new_question
			interview.save()

		return redirect('/dashboard/interviews/' + str(id))
	
	### GET REQUEST ###
	elif request.method =='GET':
		question_list = []
		questions = Question.objects.all().filter(id_interview_type=int(id)).order_by('-date_published')
		for question in questions:
			have_flow = QuestionFlow.objects.all().filter(parent=question)
			if (not have_flow.exists()) or (question.is_fork and (have_flow.count() < question.length)):
				question_list.append(question)
		
		choices_arr = []
		for question in question_list:
			if question.is_fork:
				choices = question.choices
				choices_arr += choices.split(';')

		return render(request, 'dash-add-questions.html', {
			'questions': question_list,
			'choices': choices_arr,
			'user': request.user,
			'id' : id
		})

def login_recruiter(request):
	form = LoginForm()
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect('/dashboard/')
			else:
				return render(request, 'login_recruiter.html', context = {'login_message' : 'This account is not active.', 'form':form})
		else:
			return render(request, 'login_recruiter.html', context = {'login_message' : 'Email or password are invalid.', 'form':form})  

	# GET #
	if not request.user.is_authenticated:
		return render(request, 'login_recruiter.html', context = {'form':form})
	else:
		return redirect('/dashboard/')

@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_index(request):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')
	colloqui = Interview.objects.all().order_by('-date')
	user = request.user
	return render(request, 'dashboard.html', context = {
		'colloqui' : colloqui,
		'user' : user
	})

@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_interview(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')
	interview = Interview.objects.get(pk=id)
	user = interview.user
	date = interview.date
	answers = Answer.objects.filter(interview=interview)
	comments = Comment.objects.filter(interview=interview)
	keywords = {}
	matched = MatchKeyword.objects.all().filter(interview=interview)
	for key in matched:
		value = float(key.rating)
		if value < -0.25:
			explain = 'Insufficiente'
		elif value < 0:
			explain = 'Sufficiente'
		elif value < 0.25:
			explain = 'Buono'
		else:
			explain = 'Ottimo'
		keywords[str(key.word)] = explain

	return render(request, 'interview_detail.html', context = {
		'type' 		: 	interview.type.interview_name,
		'user' 		: 	user,
		'date' 		: 	date,
		'answers' 	: 	answers,
		'comments' 	: 	comments,
		'id' 		: 	id,
		'an' 		: 	interview.analyzed,
		'keywords'	:	keywords,
		'cv_name' 	:	user.cv
	})

@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_interview_addcomment(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')
	
	interview = Interview.objects.get(pk=id)
	content = request.POST['text']
	user = request.user.first_name + ' ' + request.user.last_name
	comment = Comment.objects.create(content=content, author = user, interview = interview)
	comment.save()
	return redirect('/dashboard/'+str(id))

@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_interview_toggle_mark(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')
	
	interview = Interview.objects.get(pk=id)
	interview.analyzed = not interview.analyzed
	interview.save()
	return redirect('/dashboard/'+str(id))

@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_interview_delete(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')
	try:
		user = CandidateUser.objects.get(pk=int(id))
		user.delete()
		return redirect('/dashboard')
	except CandidateUser.DoesNotExist:
		return HttpResponse(request, 'Selected user does not exists')

	return HttpResponse(request, 'Some errors')


@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_question_edit(request, id, q_id):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')
	if request.method == 'GET':
		question = Question.objects.get(pk=int(q_id))
		return render(request, 'dash-edit-questions.html', context = {
			'action' : question.action, 
			'id' : str(id),
			'user': request.user,
			'q_id' : q_id}) 

	elif request.method == 'POST':
		if 'action' in request.POST:
			new_act = request.POST['action']
			question = Question.objects.get(pk=int(q_id))
			question.action = new_act
			question.save()
			return redirect('/dashboard/interviews/' + str(id))


@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_interview_type_list(request):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')
	types = InterviewType.objects.all()

	return render(request, 'questions-dash.html', context={
		'types'	: types,
		'user'	: request.user
		})


@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_print_interview(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')
	interview = InterviewType.objects.get(pk=int(id))
	all_question = []
	if interview.start_question:
		get_all_question(interview.start_question, all_question)

	type_list = {	
		"0" 	: "javascript",
		"1" 	:  "java",
		"2" 	:  "python", 
		"3" 	:   "php", 
		"4" 	:   "c / c++", 
		"5" 	:   "html"
	}

	link = 'https://itcinterview.it/?interview=' + str(id)
	return render(request, 'list-questions.html', context={
		'user'		: request.user,
		'questions'	: all_question,
		'interview'	: interview.interview_name,
		'id'		: str(id),
		'type_list'	: type_list,
		'link' 		: link
	})


@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_add_keywrods(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')
	
	if request.method == 'GET':
		return render(request, 'add-keyword.html', context={
			"id" : id
		})
	elif request.method == 'POST':
		if 'word' in request.POST:
			word = request.POST['word']
			interview = InterviewType.objects.get(pk=int(id))
			new_kw = KeyWords.objects.create(word=word, interviewtype=interview)
			new_kw.save()
			return redirect('/dashboard/interviews/'+str(id)+'/keywords')
	return Response(status=status.HTTP_400_BAD_REQUEST)


@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_add_question_keywrods(request, id, id_kw):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')

	if request.method == 'GET':
		keyword = KeyWords.objects.get(pk=int(id_kw))
		start_question = keyword.start_question

		parent_choice = []
		tech_flow_question = []
		if start_question:
			get_all_question(start_question, tech_flow_question)
			for question in tech_flow_question:
				have_flow = QuestionFlow.objects.all().filter(parent=question)
				if have_flow.exists():
					if question.type == 'check' and have_flow.count() < question.length:
						parent_choice.append(question)
				else:
					parent_choice.append(question)

		choices_arr = []
		for question in parent_choice:
			if question.is_fork:
				choices = question.choices
				choices_arr += choices.split(';')

		return render(request, 'add-question-keyword.html', {
			'keyword' : keyword.word,
			'questions': parent_choice,
			'choices': choices_arr,
			'user': request.user,
			'id_kw': id_kw,
			'id' : id
		})
	if request.method == 'POST':
		if not ('type' in request.POST and 'action' in request.POST ):
			return HttpResponse('Missing essentials parameters')
		
		type 		= request.POST['type']
		action 		= request.POST['action']

		if 'length' in request.POST:
			length	= request.POST['length']
		if 'lang' in request.POST:
			lang = request.POST['lang']
		if type == 'code':
			length = lang
			
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

		analyze = False
		if type == 'video':
			if 'ai' in request.POST:
				analyze = request.POST['ai']
		
		new_question = Question.objects.create(type=type, action=action, length=length, choices=choices, is_fork=is_fork, id_interview_type=int(id), to_analyze=analyze, is_technical=True)
		new_question.save()

		if 'check_parent' in request.POST:
			parents = request.POST.getlist('check_parent')
			for parent_id in parents:
				parent = Question.objects.get(pk=int(parent_id))
				flow = QuestionFlow.objects.create(parent=parent, son=new_question, choice=choice_fork )
				flow.save()

		keyword = KeyWords.objects.get(pk=int(id_kw))
		if not keyword.start_question or keyword.start_question is None:
			keyword.start_question = new_question
			keyword.save()
		
		return redirect('/dashboard/interviews/'+str(id)+'/keywords/' + str(id_kw))




@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_print_keywrods(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')

	interviewtype = InterviewType.objects.get(pk=id)
	keywords = KeyWords.objects.all().filter(interviewtype = interviewtype)

	return render(request, 'list-keywords.html', context={
		'interview'	: interviewtype.interview_name,
		'id' : id,
		'keywords' : keywords
	})


@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_print_keywrod_flow(request, id, id_kw):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')

	interview = InterviewType.objects.get(pk=int(id))
	keyword = KeyWords.objects.get(pk=int(id_kw))
	start = keyword.start_question

	title = interview.interview_name + ': ' + keyword.word
	all_question = []
	if start:
		get_all_question(start, all_question)
	type_list = {	
		"0" 	: "javascript",
		"1" 	:  "java",
		"2" 	:  "python", 
		"3" 	:   "php", 
		"4" 	:   "c / c++", 
		"5" 	:   "html"
	}

	link = 'https://itcinterview.it/?interview=' + str(id)
	return render(request, 'list-keyword-flow.html', context={
		'user'		: request.user,
		'questions'	: all_question,
		'interview'	: title,
		'id'		: str(id),
		'id_kw'		: str(id_kw),
		'type_list'	: type_list,
		'link' 		: link
	})

@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_delete_interviewtype(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')
	interview = InterviewType.objects.get(pk=int(id))
	all_question = Question.objects.all().filter(id_interview_type=int(id))
	for quest in all_question:
		quest.delete()
	interview.delete()
	return redirect('/dashboard/interviews')


@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def dashboard_edit_interviewtype(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_recruiter')
	if 'new_name' in request.POST:
		inttype = InterviewType.objects.get(pk=int(id))
		inttype.interview_name = request.POST['new_name']
		inttype.save()
		return redirect('/dashboard/interviews/'+str(id))
	else:
		return Response(status=status.HTTP_400_BAD_REQUEST)


def get_all_question(node, all_question):
	adj = QuestionFlow.objects.filter(parent=node)
	all_question.append(node)
	for flow in adj:
		if flow.son not in all_question:
			get_all_question(flow.son, all_question)

def logout_recruiter(request):
	logout(request)
	return redirect('/login_recruiter')

def logout_user(request):
	logout(request)
	return redirect('/')

@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def get_video_interview(request, name):
	if not request.user.is_authenticated:
		return HttpResponse(status=403)

	elif request.method == 'GET':
		file = Answer.objects.all().filter(choice_vid = name)
		if file.exists() and file.count() == 1:
			return FileResponse(file[0].choice_vid, status=200)
		else:
			return HttpResponse(status=404)

	return HttpResponse(status=400)



@user_passes_test(test_check_user_group, login_url="/login_recruiter/")
def get_cv_user(request, name):
	if not request.user.is_authenticated:
		return HttpResponse(status=403)

	elif request.method == 'GET':
		file = CandidateUser.objects.all().filter(cv = name)
		if file.exists() and file.count() == 1:

			temp_name = name.split("/",1)
			if len(temp_name) > 1:
				real_name = temp_name[1]
			else:
				real_name = name
			response = HttpResponse(file[0].cv, content_type="application/pdf", status=200)
			response['Content-Disposition'] = 'attachment; filename=%s' % real_name
			return response
		else:
			return HttpResponse(status=404)

	return HttpResponse(status=400)