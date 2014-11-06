from django.shortcuts import render
from django.http import HttpResponse
import datetime

from .models import Greeting

# Create your views here.
def index(request):
    return HttpResponse('Hello from Python!')


def db(request):

    # greeting = Greeting()
    # greeting.save()
    #
    # greetings = Greeting.objects.all()
    g.when=datetime.datetime.now()


    return render(request, 'db.html', {'greetings': greetings})

