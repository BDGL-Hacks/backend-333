from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from users.models import User_Profile, Event
from datetime import date


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
    if request.method == 'POST':
        if request.user.is_authenticated():
            group_events_names = request.POST.get('events_names', '')
            group_members_names = request.POST.get('member_names', '')
            if not group_events_names or not group_members_names:
                response['error'] = 'MISSING INFO'
                response['accepted'] = False
                return JsonResponse(response)
            members = []
            for member_name in group_members_names:
                members.append()
        else:
            response['error'] = 'User is not logged in'
            response['accepted'] = False
            return JsonResponse(response)
    else:
        response['error'] = 'NOT A POST REQUEST'
        response['accepted'] = False
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
def event_search(request):
    '''
    Client sends a POST request that includes information to be searched on.
    Possible information the requst can include is title, public, location
    (not implemented yet), date/time, age, price, category (not implemented
    yet), and description.
    '''
    response = {}
    # Check for errors in the function call
    if request.method != 'POST':
        response['error'] = 'NOT A POST REQUEST'
        response['accepted'] = False
        return JsonResponse(response)
    if not request.user.is_authenticated():
        response['error'] = 'User is not logged in'
        response['accepted'] = False
        return JsonResponse(response)

    # Parse request and return search results
    query = Event.objects.all()

    # TODO: there should probabily be some kind of sanitization here
    if 'title' in request.POST:
        query = query.filter(title__icontains=request.POST['title'])
    if 'public' in request.POST:
        # requests.POST['public'] should be either 0 or 1
        query = query.filter(public=int(request.POST['public']))
    if 'location' in request.POST:
        pass    # TODO
    if 'date' in request.POST:
        # Parse datetime object from request
        # Date should be formatted as follows:
        # YYYYMMDDhhmm
        year = int(request.POST['date'][:4])
        month = int(request.POST['date'][4:6])
        day = int(request.POST['date'][6:8])
        # hour = int(request.POST['date'][8:10])
        # minute = int(request.POST['date'][10:12])
        query = query.filter(time__startswith=date(year, month, day))
    if 'age' in request.POST:
        query = query.filter(age_restrictions__lte=int(request.POST['age']))
    if 'price' in request.POST:
        query = query.filter(price__lte=int(request.POST['price']))
    if 'category' in request.POST:
        pass    # TODO
    if 'description' in request.POST:
        query = query.filter(description__icontains=request.POST['description'])

    results = []
    for entry in query:
        # Remove unnecessary fields from query results
        entry = entry.to_dict()
        entry.pop('attending_list', None)
        entry.pop('created_by', None)

        # Replace foreign keys with actual names/values
        invited = entry.pop('invite_list', None)
        invited_detail = []
        for invitee in invited:
            user_profile = User_Profile.objects.get(pk=invitee.id)
            detail = {
                'id': invitee.id,
                'username': user_profile.user.username,
                'first_name': user_profile.user.first_name,
                'last_name': user_profile.user.last_name
            }
            invited_detail.append(detail)
        entry['invite_list'] = invited_detail

        admin = entry.pop('admin', None)
        admin = User_Profile.objects.get(pk=admin.id)
        admin_detail = {
            'id': admin.id,
            'username': admin.user.username,
            'first_name': admin.user.first_name,
            'last_name': admin.user.last_name
        }
        entry['admin'] = admin_detail

        # Save the updated entry
        results.append(entry)

    # Return results
    response['accepted'] = True
    response['results'] = results
    return JsonResponse(response)


@csrf_exempt
def user_search(request):
    pass
