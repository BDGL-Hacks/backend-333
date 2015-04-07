from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from users.models import User_Profile, Event, Group
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
            return JsonResponse(response)

        # checks if email is used
        if User.objects.filter(email=user_email):
            response['error'] = 'That email is being used. Please use another email'
            response['accepted'] = False
            return JsonResponse(response)

        # Create the new account and a profile for that account
        # TODO: consider sanitizing input
        user = User.objects.create_user(username=user_email, password=user_pswd,
                                        email=user_email, first_name=user_fn,
                                        last_name=user_ln)

        # Add new user to the database
        User_Profile(user=user).save()
        response['accepted'] = True
        return JsonResponse(response)
    else:
        response['error'] = 'NOT A POST REQUEST'
        response['accepted'] = False
        return JsonResponse(response)


@csrf_exempt
def create_group(request):
    response = {}
    # Verify that we are posting data
    if request.method != 'POST':
        response['error'] = 'Must be a POST request'
        response['accepted'] = False
        return JsonResponse(response)

    # Verify that the user is logged in
    if not request.user.is_authenticated():
        response['error'] = 'User is not logged in'
        response['accepted'] = False
        return JsonResponse(response)

    # grab the User_Profile of the person logged in
    user = request.user.user_profile

    # grab the post data
    # Split the first two by commas
    events_ids = request.POST.get('events_ids', '').split(',')
    invite_list = request.POST.get('invite_list', '').split(',')

    # add the user to the invite list (A user is invited to their own group)
    invite_list.append(user.user.username)
    group_name = request.POST.get('title', '')

    # Check for mandatory data
    if not events_ids or not group_name:
        response['error'] = 'MISSING INFO'
        response['accepted'] = False
        return JsonResponse(response)

    # Create and save the group
    group = Group(created_by=user, title=group_name)
    group.save()

    # Make the chat channel with the group id
    group.chat_channel = "GroupChat" + str(group.id)

    # Grab all of the events from the database
    for num in events_ids:
        # Get the proper id
        e = Event.objects.filter(id=int(num))

        # return false if the event doesn't exist
        if not e:
            response['error'] = 'One of your events is not correct'
            response['accepted'] = False

            # delete the group (TODO: check to make sure nothing is dangling)
            group.delete()
            return JsonResponse(response)

        group.events.add(e[0])

    # grab all of the User_Profiles to be invited
    for name in invite_list:
        if not name:
            continue

        # get the django User object
        u = User.objects.filter(username=name)

        # Get the actual User_Profile object
        if u:
            u = u[0].user_profile
        if not u:
            response['error'] = 'One of your invitees is not a user'
            response['accepted'] = False
            group.delete()
            return JsonResponse(response)

        group.invited_members.add(u)
        # TODO add invites and remove the below line
        group.group_members.add(u)
        u.groups_current.add(group)
        u.save()

    group.save()
    response['accepted'] = True
    return JsonResponse(response)


@csrf_exempt
def login_view(request):
    response = {}
    if request.user.is_authenticated():
        response['error'] = 'You are already logged in'
        response['accepted'] = False
        return JsonResponse(response)

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if not username or not password:
            response['error'] = 'MISSING INFO'
            response['accepted'] = False
            return JsonResponse(response)

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                response['accepted'] = True
                return JsonResponse(response)
            else:
                response['error'] = 'Your account has been disabled'
                response['accepted'] = False
                return JsonResponse(response)
        else:
            response['error'] = 'Wrong Username or Password'
            response['accepted'] = False
            return JsonResponse(response)
    else:
        response['error'] = 'NOT A POST REQUEST'
        response['accepted'] = False
        return JsonResponse(response)


@csrf_exempt
def user_search(request):
    pass
