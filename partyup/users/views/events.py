from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from users.models import Event, User_Profile
from datetime import date, datetime


# Check that the given request is a POST request and comes from a user that is
# logged in. Returns a JsonResponse object containing an error message if the
# request is invalid. Return None otherwise.
def validate_request(request):
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
def create_event(request):
    '''
    Create a new event object from the given request and add it to the
    database.

    The function takes a POST request that contains the following parameters:
    title, public, age_restrictions, price, invite_list, and time. Of those
    parameters, the only required parameters are title and time.
    '''
    # intialize the end response and the information for event
    response = {}
    event_data = {}
    error = validate_request(request)
    if error:
        return error

    # Grab the post data and the user who is logged in
    data = request.POST
    user = request.user.user_profile

    # fill the event fields
    event_data['title'] = data.get('title', '')
    event_data['public'] = data.get('public', '')
    event_data['age_restrictions'] = data.get('age-restrictions', 0)
    event_data['admin'] = user
    event_data['created_by'] = user
    event_data['price'] = data.get('price', 0)

    # split the invite list by commas
    invite_list = data.get('invite_list', '').split(',')
    # add the logged in user to the invite list
    invite_list.append(user.user.username)
    time = data.get('time', '')

    # check for missing POST information
    if not event_data['title'] or not time:
        response['error'] = 'You are missing information'
        response['accepted'] = False
        return JsonResponse(response)

    # change time format
    # The time included in the POST request should take the form
    # YYYYMMDDhhmm
    event_data['time'] = datetime(int(time[0:4]), int(time[4:6]),
                                  int(time[6:8]), int(time[8:10]),
                                  int(time[10:12]))

    # create and save the actual event
    event = Event(**event_data)
    event.save()

    # add the event to the user's admin list
    user.event_admin_list.add(event)
    user.save()

    # invite all of the invited users
    for name in invite_list:
        # ignore blank entries
        if not name:
            continue

        u = User.objects.filter(username=name)
        if u:
            u = u[0].user_profile
        else:
            # Error if user doesn't exist. In theory, this case should only
            # happen is someone is trying to hack the API.
            response['error'] = 'One of your invitees is not a user'
            response['accepted'] = False
            event.delete()
            return JsonResponse(response)

        event.invite_list.add(u)
        u.event_invite_list.add(event)
        # TODO add invites and remove the below line
        event.attending_list.add(u)
        u.event_attending_list.add(event)
        u.save()

    event.save()
    response['accepted'] = True
    return JsonResponse(response)


@csrf_exempt
def event_search(request):
    '''
    This function is a general search across all events in the database.

    Takes a POST request that includes information to be searched on.
    Possible information the requst can include is title, public, location
    (not implemented yet), date/time, age, price, category (not implemented
    yet), and description.
    '''
    response = {}
    error = validate_request(request)
    if error:
        return error

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
