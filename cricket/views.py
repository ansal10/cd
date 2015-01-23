from django.shortcuts import render
from django.http import HttpResponse
import datetime

from .models import Greeting

# Create your views here.
def index(request):
    return HttpResponse('cricket from Python!')


def db(request):

    # greeting = Greeting()
    # greeting.save()
    #
    # greetings = Greeting.objects.all()


    return render(request, 'db.html', {'greetings': {'when':datetime.datetime.now()}})

