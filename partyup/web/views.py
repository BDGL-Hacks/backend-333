from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


def homepage(request):
    '''
    Render the home page.
    '''
    print "in wrong"
    return render(request, 'web/index.html', {'server': settings.DESTINATION})


def groups_home(request):
    print "here"
    return render(request, 'web/group-home.html', {'server': settings.DESTINATION})
