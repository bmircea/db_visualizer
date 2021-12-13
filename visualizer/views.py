from django.http import HttpResponse, response

from .models import Question

def index(request):
    