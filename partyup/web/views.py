from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


def homepage(request):
    '''
    Render the home page.
    '''
    return render(request, 'web/index.html')


def groups_home(request):
    return render(request, 'web/group-home.html')


def groups_events(request):
    return render(request, 'web/group-events.html', {'server': settings.DESTINATION})

def groups_ping(request):
    return render(request, 'web/group-ping.html')
