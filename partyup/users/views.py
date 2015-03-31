from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from users.models import User_Profile
import json

@csrf_exempt
def register(request):
    response = {}
    if request.method == 'POST':
        user_data = request.POST

        user_email = user_data.get('email', '')
        user_fn = user_data.get('first_name', '')
        user_ln = user_data.get('last_name', '')
        user_pswd = user_data.get('password', '')

        # Ensure all parameters were included in the request
        if not user_email or not user_fn or not user_ln or not user_pswd:
            response['error'] = "MISSING INFO"
            response['accepted'] = False
            return HttpResponse(json.dumps(response),
                                content_type="application/json")

        # checks if email is used
        if User.objects.filter(email=user_email):
            response['error'] = 'That email is being used. Please use another email'
            response['accepted'] = False
            return HttpResponse(json.dumps(response),
                                content_type="application/json")

        # Create the new account and a profile for that account
        # TODO: consider sanitizing input
        user = User.objects.create_user(username=user_email, password=user_pswd,
                                        email=user_email, first_name=user_fn,
                                        last_name=user_ln)
        
        # Add new user to the database
        User_Profile(user=user).save()

        response['accepted'] = True
        return HttpResponse(json.dumps(response),
                            content_type="application/json")
    else:
        response['error'] = 'NOT A POST REQUEST'
        response['accepted'] = False
        return HttpResponse(json.dumps(response),
                            content_type="application/json")

@csrf_exempt
def create_group(request):
    response = {}
    if request.method == 'POST':
        if request.user.is_authenticated():
            group_events_names  = request.POST.get('events_names', '')
            group_members_names = request.POST.get('member_names', '')
            if not group_events_names or not group_members_names:
                response['error'] = 'MISSING INFO'
                response['accepted'] = False
                return HttpResponse(json.dumps(response),
                                content_type='application/json')
            members = []
            for member_name in group_members_name:
                members.append()
        else:
            response['error'] = 'User is not logged in'
            response['accepted'] = False
            return HttpResponse(json.dumps(response),
                                content_type='application/json')
    else:
        response['error'] = 'Must be a POST request'
        response['accepted'] = False
        return HttpResponse(json.dumps(response),
                                content_type='application/json')

@csrf_exempt
def login_view(request):
    response = {}
    if request.user.is_authenticated():
        response['error'] = 'You are already logged in'
        response['accepted'] = False
        return HttpResponse(json.dumps(response),
                            content_type="application/json")

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if not username or not password:
            response['error'] = 'MISSING INFO'
            response['accepted'] = False
            return HttpResponse(json.dumps(response),
                                content_type='application/json')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                response['accepted'] = True
                return HttpResponse(json.dumps(response),
                                    content_type="application/json")
            else:
                response['error'] = 'Your account has been disabled'
                response['accepted'] = False
                return HttpResponse(json.dumps(response),
                                    content_type="application/json")
        else:
            response['error'] = 'Wrong Username or Password'
            response['accepted'] = False
            return HttpResponse(json.dumps(response),
                                content_type="application/json")
    else:
        response['error'] = 'NOT A POST REQUEST'
        response['accepted'] = False
        return HttpResponse(json.dumps(response),
                            content_type="application/json")
