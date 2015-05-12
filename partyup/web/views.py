from django.shortcuts import render


def homepage(request):
    '''
    Render the home page.
    '''
    return render(request, 'web/index.html')


def landingpage(request):
    '''
    Render the home page.
    '''
    return render(request, 'web/landingpage.html')

def groups_home(request):
    return render(request, 'web/group-home.html')


def groups_events(request):
    return render(request, 'web/group-events.html')


def groups_ping(request):
    return render(request, 'web/group-ping.html')
