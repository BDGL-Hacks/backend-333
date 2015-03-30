from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from users.models import Person, User_Profile
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
        user = User.objects.create_user(username=user_email, password=user_pswd,
                                        email=user_email, first_name=user_fn,
                                        last_name=user_ln)
        profile = User_Profile()
        profile.save()

        # Add new user to the database
        Person(user=user, profile=profile).save()

        response['accepted'] = True
        return HttpResponse(json.dumps(response),
                            content_type="application/json")
    else:
        response['error'] = 'NOT A POST REQUEST'
        response['accepted'] = False
        return HttpResponse(json.dumps(response),
                            content_type="application/json")


@csrf_exempt
def login_view(request):
    response = {}
    if request.user.is_authenticated():
        response['error'] = 'You are already logged in'
        response['accepted'] = False
        return HttpResponse(json.dumps(response),
                            content_type="application/json")

    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
        except KeyError:
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
