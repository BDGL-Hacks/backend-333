from base64 import b64encode
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from hashlib import md5
from users.models import User_Profile, Ping
from users.views.push import add_device
import pictures


def _validate_request(request):
    '''
    Check that the given request is a POST request and comes from a user that
    is logged in. Returns a JsonResponse object containing an error message if
    the request is invalid. Return None otherwise.
    '''
    response = {}
    # Check that the request is a POST
    if request.method != 'POST':
        response['error'] = 'NOT A POST REQUEST'
        response['accepted'] = False
        return JsonResponse(response)
    # Check that the user is logged in
    if not request.user.is_authenticated():
        response['error'] = 'User is not logged in'
        response['accepted'] = False
        return JsonResponse(response)
    return None


@csrf_exempt
def register(request):
    '''
    Registers a new user. Takes a user's first and last name, their email, and
    a password
    '''
    response = {}
    if request.method == 'POST':
        user_data = request.POST

        # All emails lowercase
        user_email = str(user_data.get('email', '')).lower()
        user_fn = user_data.get('first_name', '')
        user_ln = user_data.get('last_name', '')
        user_pswd = user_data.get('password', '')

        # Ensure all parameters were included in the request
        if not user_email or not user_fn or not user_ln or not user_pswd:
            response['error'] = "MISSING INFO"
            response['accepted'] = False
            return JsonResponse(response)

        # Hash the email to create a unique username that is sure to be less
        # than 30 characters long (the size of the username field in the Django
        # User model).
        # Base64 encode to convert to ascii string of length less than 30
        # characters
        username = b64encode(md5(user_email).digest())
        if User.objects.filter(username=username):
            # Make sure that match is not a hash collision
            # checks if email is used
            if User.objects.filter(email=user_email):
                response['error'] = 'That email is being used. Please use another email'
                response['accepted'] = False
                return JsonResponse(response)
            else:
                # hash collision
                response['error'] = 'There is a problem creating your account. \
                    Please email blawson@princeton.edu to resolve the issue \
                    and to receive a $20 gift card.'
                response['accepted'] = False
                return JsonResponse(response)

        # Create the new account and a profile for that account
        user = User.objects.create_user(username=username, password=user_pswd,
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
def login_view(request):
    response = {}
    if request.user.is_authenticated():
        response['error'] = 'You are already logged in'
        response['accepted'] = False
        return JsonResponse(response)

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        deviceID = request.POST.get('deviceID', '')
        if not username or not password:
            response['error'] = 'MISSING INFO'
            response['accepted'] = False
            return JsonResponse(response)

        # Hash username
        username = b64encode(md5(username).digest())
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:

                # Save their IOS device
                if deviceID:
                    deviceID = str(deviceID)
                    print (deviceID)
                    deviceID = deviceID.translate(None, '<> ')
                    print deviceID
                    error = add_device(deviceID, user.user_profile)
                    if error:
                        return error

                # Finally log them in
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


def _format_search_results(queryset):
    '''
    Takes a queryset of user_profiles and returns a
    formatted json
    '''
    results = []
    for entry in queryset:
        if hasattr(entry, 'user_profile'):
            entry = entry.user_profile.to_dict()
            results.append(entry)
    return results


@csrf_exempt
def user_search(request):
    ''' 
    Searches through all users and returns users who's email, last name, or first name
    match each of the terms in a given string.
    Terms in the string are seperated by spaces
    '''
    response = {}

    error = _validate_request(request)
    if error:
        return error

    query = User.objects.all()

    if 'search' in request.POST:
        # Split the search into terms
        terms = request.POST['search'].split(' ')
        for term in terms:
            if term:
                first = query.filter(first_name__icontains=term)
                last = query.filter(last_name__icontains=term)
                username = query.filter(email__icontains=term)
                # a query is the logical OR combination of all searches
                query = first | last | username

        results = _format_search_results(query)
        response = {
            'accepted': True,
            'results': results
        }
        return JsonResponse(response)
    else:
        response['error'] = 'MISSING INFORMATION'
        response['accepted'] = False
        return JsonResponse(response)


@csrf_exempt
def user_batch(request):
    ''' 
    Will return the first 10 users in the database
    '''
    response = {}
    error = _validate_request(request)
    if error:
        return error

    query = User.objects.all()[0:10]
    results = _format_search_results(query)
    response = {
        'accepted': True,
        'results': results
    }
    return JsonResponse(response)


@csrf_exempt
def user_picture_upload(request):
    '''
    Upload a picture for the given user.
    '''
    error = _validate_request(request)
    if error:
        return error
    if not request.FILES or not request.FILES['picture']:
        message = 'No picture attached'
        return JsonResponse({'accepted': False, 'error': message})

    # Upload the picture
    profile = User_Profile.objects.get(user=request.user)
    pictures.upload_user(profile, request.FILES['picture'])
    return JsonResponse({'accepted': True})


@csrf_exempt
def user_picture_delete(request):
    '''
    Delete the given user's picture.
    '''
    error = _validate_request(request)
    if error:
        return error
    profile = User_Profile.objects.get(user=request.user)
    pictures.delete_user(profile)
    return JsonResponse({'accepted': True})

@csrf_exempt
def user_ping_get(request):
    '''
    Return all existing pings for the given user.
    '''
    response = {'accepted': False}
    error = _validate_request(request)
    if error:
        return error

    # Validate the request
    user = request.user.user_profile
    pings = Ping.objects.filter(user=user, response=False)
    results = []
    for p in pings:
        results.append(p.to_dict())

    # Exit success
    response['accepted'] = True
    response['pings'] = results
    return JsonResponse(response)
