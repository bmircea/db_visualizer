from django.http import HttpResponse, response
from django.template import loader
from .models import Question

def index(request):
    dbs = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('visualizer/index.html')
    context = {
        'db_names': ['A', 'B'],
    }
    return HttpResponse(template.render(context, request))

def db(request, db_id):
    rows = {} # Get rows from db
    template = loader.get_template('visualizer/db.html')
    context = {}
    return HttpResponse(template.render(context, request))