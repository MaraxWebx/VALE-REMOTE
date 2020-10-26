from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from app.models import *
from app.form import *
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from app.serializers import *

# Create your views here.
def upload_view(request):
	form = VideoModelForm()
	return render(request, 'upload_test.html', {'form':form})


def index(request):
	if request.session.get('is_reg', False):
		return render(request, 'index.html')
	return render(request, 'credentials.html')

def interview(request):
	if request.session.get('is_reg', False):
		return render(request, 'index.html')
	else:
		return redirect('/')

def video_preview(request):
	model = VideoModel.objects.all()
	return render(request, 'videos.html', {'query':model})

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def test_rest(request):
	if request.method == 'GET':
		question = QuestionSerializer(Question.objects.get(pk=1))
		return Response(question.data)
	elif request.method == 'POST':
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			if not request.session.get('is_reg', False):
				print('New user')
				serializer.save() # <-- Da cambiare. Queste informazioni dovranno essere salvate più avanti.
				request.session['is_reg'] = True
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			print('Already registered')
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'OPTIONS':
		return Response(None, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def upload_requests(request):
	if request.method == 'POST':
		# Add code here
		return Response(request.data, status=status.HTTP_201_CREATED)

class VideoUploadView(APIView):
	parser_classes = [MultiPartParser]
	permission_classess = ([])
	authentication_classes = ([])

	def post(self, request, *args, **kwargs):
		file = request.data.dict()['file']
		model = VideoModel.objects.create(video=file)
		model.save()
		return Response(status=status.HTTP_201_CREATED)

	def get(self, request, *args, **kwargs):
		form = VideoModelForm()
		return render(request, 'upload_test.html', {'form':form} )
