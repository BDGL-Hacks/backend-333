from django.http import HttpResponse
from django.shortcuts import render


def homepage(request):
    '''
    Render the home page.
    '''
    return render(request, 'web/index.html')
