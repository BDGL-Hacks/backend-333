from base64 import b64encode
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from hashlib import md5
from users.models import User_Profile


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
        # TODO: consider sanitizing input
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
        if not username or not password:
            response['error'] = 'MISSING INFO'
            response['accepted'] = False
            return JsonResponse(response)

        # Hash username
        username = b64encode(md5(username).digest())
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


def _format_search_results(queryset):
    results = []
    for entry in queryset:
        if hasattr(entry, 'user_profile'):
            entry = entry.user_profile.to_dict()
            results.append(entry)
    return results


@csrf_exempt
def user_search(request):
    response = {}

    error = _validate_request(request)
    if error:
        return error

    query = User.objects.all()

    if 'search' in request.POST:
        terms = request.POST['search'].split(' ')
        for term in terms:
            if term:
                first = query.filter(first_name__icontains=term)
                last = query.filter(last_name__icontains=term)
                username = query.filter(email__icontains=term)
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
