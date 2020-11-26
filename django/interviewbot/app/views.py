from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
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
	if request.method == 'GET':
		if request.session.get('is_reg', False):
			return redirect('/interview/')
		else:
			request.session.clear_expired()
			request.session.flush()
			request.session.set_expiry(300)
			request.session['is_reg'] = False
			interviewtype_id = request.GET.get('interview', -1)
			if int(interviewtype_id) > 0:
				interviewtype = InterviewType.objects.filter( pk = int(interviewtype_id))
				if interviewtype.exists() and interviewtype.count() == 1:
					request.session['interview'] = interviewtype_id
				else:
					request.session['interview'] = -1
			return render(request, 'credentials.html')

def interview(request):
	if  request.session.get('is_reg', False) and CandidateUser.objects.filter(pk=request.session.get('user_id', -1)).count() > 0:
		return render(request,'index.html')
	else:
		request.session['is_reg'] = False
		request.session['user_id'] = -1
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
			type = InterviewType.objects.get(pk = int(request.session.get('interview', 1)))
			interview = Interview.objects.create(user=new_user, type = type)
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
				if int(request.session.get('interview', -1 )) > 0:
					interviewtype = InterviewType.objects.filter(pk = int(request.session['interview']))
					if interviewtype.exists() and interviewtype.count() == 1:
						first_question = interviewtype[0].start_question
						nq_serialized = QuestionSerializer(first_question)
						return Response(nq_serialized.data, status=status.HTTP_200_OK)
				first_question = Question.objects.get(pk=56)
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

		if dict['answer_vid'] == 'to_upload':
			request.session['last_ans_id'] = answer.id
		else:
			request.session['last_ans_id'] = -1

		# Generazione prossima domanda

		next_question = self.get_next_question(question_id, answer_text, request.session)

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

	def get_next_question(self, id, answer, session):

		question = Question.objects.get(id=id)
		if question is not None:
			if question.type == 'check' or question.type == 'code' or not question.to_analyze:
				if int(session.get('last_base_quest',-1)) < 0  or not session.get('have_forked', False):
					session['last_base_quest'] = id
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
						for flow in flows:
							if flow.choice == "":
								return flow.son
				else:
					if not question.is_technical:
						session['last_base_quest'] = -1
					return 0
			else:
				if not session.get('have_forked', False):
					session['last_base_quest'] = id
				session['have_forked'] = True
				
				analyzer = TextAnalyzer(answer)
				analyze_results = analyzer.analyze()
				

				filter = Filter()
				filter_results = filter.execute(analyze_results)
				
				if not filter_results:
					last_id = session.get('last_base_quest', -1)
					if int(last_id) > 0:
						question = Question.objects.get(id=id)
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

				sentiment = SA.execute(filter_results)

				key_max = ""
				value_max = -999999999
				interview = Interview.objects.get(pk=int(session['interview_id']))
				for key in sentiment:
					print("########### VALUE:", key, "POL:", sentiment[key], "##############")
					try:
						old_match = MatchKeyword.objects.get(word=str(key), interview=interview)
						old_match.rating = float(old_match.rating) + float(sentiment[key])
						old_match.save()
					except MatchKeyword.DoesNotExist:
						new_match = MatchKeyword.objects.create(word=str(key), rating = float(sentiment[key]), interview=interview)
						new_match.save()
					except MatchKeyword.MultipleObjectsReturned:
						print('Cant save this keyword polarity cause multiple entry with same name and interview in database. Check the database instances.')

					if sentiment[key] > value_max:
						value_max = sentiment[key]
						key_max = key

				if value_max < -0.25:
					last_id = session.get('last_base_quest', -1)
					if int(last_id) > 0:
						question = Question.objects.get(id=id)
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
				interviewtype = InterviewType.objects.get(pk = int(session.get('interview',1)))
				kw_question = KeyWords.objects.filter(word=key_max, interviewtype = interviewtype)[0]
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


def add_interview(request):
	if not request.user.is_authenticated:
		return redirect('/login_rectruiter')

	if request.method=='GET':
		return render(request, 'add-interview.html')
	elif request.method=='POST':
		if not 'action' in request.POST:
			return HttpResponse('Missing interview name')
		name = request.POST['action']
		new_interview_type = InterviewType.objects.create(interview_name = name, addedby=(str(request.user.first_name) + ' ' + str(request.user.last_name)))
		new_interview_type.save()
		return redirect('/dashboard/interviews')


def add_question(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_rectruiter')
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
		elif 'lang' in request.POST:
			length = request.POST['lang']
		
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
		
		new_question = Question.objects.create(type=type, action=action, length=length, choices=choices, is_fork=is_fork, id_interview_type=int(id))
		new_question.save()

		if 'check_parent' in request.POST:
			parents = request.POST.getlist('check_parent')
			for parent_id in parents:
				parent = Question.objects.get(pk=int(parent_id))
				flow = QuestionFlow.objects.create(parent=parent, son=new_question, choice=choice_fork )
				flow.save()

		return HttpResponse('New question added with id: ' + str(new_question.id))
	
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


def dashboard_index(request):
	if not request.user.is_authenticated:
		return redirect('/login_rectruiter')
	colloqui = Interview.objects.all().order_by('-date')
	user = request.user
	return render(request, 'dashboard.html', context = {
		'colloqui' : colloqui,
		'user' : user
	})


def dashboard_interview(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_rectruiter')
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
		'keywords'	:	keywords
	})

def dashboard_interview_addcomment(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_rectruiter')
	
	interview = Interview.objects.get(pk=id)
	content = request.POST['text']
	user = request.user.first_name + ' ' + request.user.last_name
	comment = Comment.objects.create(content=content, author = user, interview = interview)
	comment.save()
	return redirect('/dashboard/'+str(id))

def dashboard_interview_toggle_mark(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_rectruiter')
	
	interview = Interview.objects.get(pk=id)
	interview.analyzed = not interview.analyzed
	interview.save()
	return redirect('/dashboard/'+str(id))

def dashboard_interview_delete(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_rectruiter')
	try:
		user = CandidateUser.objects.get(pk=int(id))
		user.delete()
		return redirect('/dashboard')
	except CandidateUser.DoesNotExist:
		return HttpResponse(request, 'Selected user does not exists')

	return HttpResponse(request, 'Some errors')

def dashboard_question_edit(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_rectruiter')
	if request.method == 'GET':
		question = Question.objects.get(pk=int(id))
		return render(request, '', context = {'question' : question})  ### <-- Add edit template
	elif request.method == 'POST':
		if 'action' in request.POST:
			new_act = request.POST['action']
			question = Question.objects.get(pk=int(id))
			question.action = new_act
			question.save()
			return redirect('/dashboard/interview/' + str(id))


def dashboard_interview_type_list(request):
	if not request.user.is_authenticated:
		return redirect('/login_rectruiter')
	types = InterviewType.objects.all()

	return render(request, 'questions-dash.html', context={
		'types'	: types,
		'user'	: request.user
		})

	# get the list of interview type's

def dashboard_print_interview(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_rectruiter')
	interview = InterviewType.objects.get(pk=int(id))
	all_question = []
	if interview.start_question:
		get_all_question(interview.start_question, all_question)

	link = 'https://itcinterview.it/?interview=' + str(id)
	return render(request, 'list-questions.html', context={
		'user'		: request.user,
		'questions'	: all_question,
		'interview'	: interview.interview_name,
		'link' 		: link
	})

def dashboard_delete_interviewtype(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_rectruiter')
	interview = InterviewType.objects.get(pk=int(id))
	question = interview.start_question
	all_question = []
	if question:
		get_all_question(question, all_question)
		for quest in all_question:
			quest.delete()
	interview.delete()
	return render('/dashboard/interviews')

def dashboard_edit_interviewtype(request, id):
	if not request.user.is_authenticated:
		return redirect('/login_rectruiter')


def get_all_question(node, all_question):
	adj = QuestionFlow.objects.filter(parent=node)
	all_question.append(node)
	for flow in adj:
		if flow.son not in all_question:
			get_all_question(flow.son, all_question)


def logout_recruiter(request):
	logout(request)
	return redirect('/login_rectruiter')

