from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from users.models import User_Profile, Event
import json
from datetime import datetime

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
    if request.method != 'POST':
        response['error'] = 'Must be a POST request'
        response['accepted'] = False
        return HttpResponse(json.dumps(response),
                                content_type='application/json')
    if not request.user.is_authenticated():
        response['error'] = 'User is not logged in'
        response['accepted'] = False
        return HttpResponse(json.dumps(response),
                            content_type='application/json')
    group_events_names  = request.POST.get('events_names', '')
    group_members_names = request.POST.get('member_names', '')
    group_name = request.POST.get('group_name', '')
    if not group_events_names or not group_members_names or not group_name:
        response['error'] = 'MISSING INFO'
        response['accepted'] = False
        return HttpResponse(json.dumps(response),
                            content_type='application/json')
    group = Group(created_by=request.user, group_name=group_name)
    group.save()    
    group.chat_channel("GroupChat" + str(id))
    for event in group_events_names:
        e = Event.objects.filter(id=event)
    for name in group_members_names:
        u = User.objects.filter(username=name)
        if u:
            u = u.user_profile
        if not u:
            response['error'] = 'One of your invitees is not a user'
            response['accepted'] = False
            group.delete()
            return HttpResponse(json.dumps(response),
                                content_type='application/json')
        group.invited_members.add(u)
        #TODO add invites and remove the below line
        group.group_members.add(u)
        u.groups_current(event)
        u.save()
    group.save()

@csrf_exempt
def create_event(request):
    if not request.user.is_authenticated():
        response['error'] = 'You must log in to view this page'
        response['accepted'] = False
        return HttpResponse(json.dumps(response),
                                content_type='application/json')
    if request.method != 'POST':
        response['error'] = 'Must be a POST request'
        response['accepted'] = False
        return HttpResponse(json.dumps(response),
                                content_type='application/json')
    data = request.POST
    user = request.user.user_profile
    response = {}
    event_data = {}
    event_data['title'] = data.get('title', '')
    event_data['public'] = data.get('public', '')
    event_data['age_restrictions'] = data.get('age-restrictions', 0)
    event_data['admin'] = user
    event_data['created_by'] = user
    event_data['price'] = data.get('price', 0)
    invite_list = data.get('invite_list', '').split(',')
    invite_list.append(user.user.username)
    time = data.get('time', '')
    if not event_data['title']  or not time:
        response['error'] = 'You are missing information'
        response['accepted'] = False
        return HttpResponse(json.dumps(response),
                            content_type='application/json')
    event_data['time'] = datetime(int(time[0:4]), int(time[4:6]), int(time[6:8]), int(time[8:10]), int(time[10:12]))
    event = Event(**event_data)
    event.save()
    user.event_admin_list.add(event)
    user.save()
    for name in invite_list:
        # ignore blank entries
        if not name:
            continue
        u = User.objects.filter(username=name)
        if u:
            u = u[0].user_profile
        if not u:
            response['error'] = 'One of your invitees is not a user'
            response['accepted'] = False
            event.delete()
            return HttpResponse(json.dumps(response),
                                content_type='application/json')
        event.invite_list.add(u)
        u.event_invite_list.add(event)
        #TODO add invites and remove the below line
        event.attending_list.add(u)
        u.event_attending_list.add(event)
        u.save()
    event.save()
    response['accepted'] = True
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
