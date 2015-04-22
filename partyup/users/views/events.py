from datetime import date, datetime
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import Event, User_Profile
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
def event_create(request):
    '''
    Create a new event object from the given request and add it to the
    database.

    The function takes a POST request that contains the following parameters:
    title, public, age_restrictions, price, invite_list, and time. Of those
    parameters, the only required parameters are title and time.
    '''
    # initialize the end response and the information for event
    response = {}
    event_data = {}
    error = _validate_request(request)
    if error:
        return error

    # Grab the post data and the user who is logged in
    data = request.POST
    user = request.user.user_profile

    # fill the event fields
    event_data['title'] = data.get('title', '')
    event_data['public'] = data.get('public', True)
    event_data['description'] = data.get('description', '')
    event_data['age_restrictions'] = data.get('age_restrictions', 0)
    event_data['admin'] = user
    event_data['created_by'] = user
    event_data['price'] = data.get('price', 0)
    event_data['location_name'] = data.get('location_name', '')
    # split the invite list by commas
    invite_list = data.get('invite_list', '').split(',')
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

    # add the event to the user's admin + attending list
    user.event_admin_list.add(event)
    user.event_attending_list.add(event)
    event.attending_list.add(user)
    user.save()

    # invite all of the invited users
    for name in invite_list:
        # ignore blank entries
        if not name:
            continue

        u = User.objects.filter(email=name)
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
        u.save()

    event.save()
    response['accepted'] = True
    response['id'] = event.id
    return JsonResponse(response)


def _format_search_results(queryset):
    '''
    Takes a Django QuerySet object containing Events or a list of Events.
    Returns a list of dictionaries containing information for each of the
    events in the queryset.
    '''
    results = []
    for entry in queryset:
        # Remove unnecessary fields from query results
        entry = entry.to_dict()
        entry.pop('created_by', None)

        # Replace invite_list foreign keys with actual names/values
        invited = entry.pop('invite_list', None)
        invited_detail = []
        for invitee in invited:
            user_profile = User_Profile.objects.get(pk=invitee.id)
            invited_detail.append(user_profile.to_dict())
        entry['invite_list'] = invited_detail

        # Repeat attending_list foreign keys with actual user information
        attending = entry.pop('attending_list', None)
        attending_detail = []
        for attendee in attending:
            user_profile = User_Profile.objects.get(pk=attendee.id)
            attending_detail.append(user_profile.to_dict())
        entry['attending_list'] = attending_detail

        # Replace admin foreign key with the actual admin
        admin = entry.pop('admin', None)
        admin = User_Profile.objects.get(pk=admin.id)
        entry['admin'] = admin.to_dict()

        # Save the updated entry
        results.append(entry)
    return results


@csrf_exempt
def event_search(request):
    '''
    This function is a general search across all events in the database.

    Takes a POST request that includes information to be searched on.
    Possible information the request can include is title, public, location
    (not implemented yet), date/time, age, price, category (not implemented
    yet), and description.

    TODO: Modify so it accepts a time parameter that queries just by time of
    day.
    TODO: Limit number of results returned
    '''
    error = _validate_request(request)
    if error:
        return error

    # Parse request and return search results
    query = Event.objects.all()

    # TODO: there should probably be some kind of sanitation here
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

    # Parse the output and get a list of dicts back
    results = _format_search_results(query)

    # Return results
    response = {
        'accepted': True,
        'results': results
    }

    return JsonResponse(response)


@csrf_exempt
def event_get(request):
    '''
    This function is meant to provide an easy way to query events that are
    frequently needed by a given user. That is, events created by the user,
    events the user is attending, and events the user has been invited to.

    Takes a POST request that contains the parameter 'type'. 'type' should be
    the type of events that are being queried. 'type' may be one of three
    values: 'invited' (returns events created by the given user), 'attending'
    (returns events the given user is attending), or 'created' (returned events
    created by the given user). Note that the parameter may include multiple
    values for type. For example, "type=attending&type=created" is a valid
    request.

    Returns a JSON in the form [{"accepted": true, "invited": [<JSON with
    events user is invited to>], "attending": [<JSON with events the user is
    attending>], "created": [<JSON with events the user created>]}]. Note that
    only the requested fields will be included in the JSON (e.g. if the request
    does not ask for events the user created, the events the user created will
    not be returned).
    '''
    error = _validate_request(request)
    if error:
        return error

    # Check the fields in the request
    response = {}
    for t in request.POST.getlist('type'):
        user = request.user.user_profile
        if t == 'attending':
            result = user.event_attending_list.all()
        elif t == 'created':
            result = Event.objects.all().filter(created_by=user)
        elif t == 'invited':
            result = user.invite_list.all()
        else:
            return JsonResponse({'accepted': False, 'error': 'Invalid type'})

        # Replace the foreign keys in the result with the actual events and
        # then format those events before returning them to the client.
        events = [Event.objects.get(pk=event.id) for event in result]
        response[t] = _format_search_results(events)

    response['accepted'] = True
    return JsonResponse(response)


@csrf_exempt
def event_getid(request):
    '''
    Lets client search for events by id. Returns the requested event if it
    exists.
    '''
    error = _validate_request(request)
    if error:
        return error

    if 'event' not in request.POST:
        return JsonResponse({'accepted': False, 'error': 'MISSING INFO'})

    event = Event.objects.get(pk=request.POST['event'])
    results = _format_search_results([event])
    response = {
        'accepted': True,
        'event': results[0],
    }
    return JsonResponse(response)


@csrf_exempt
def event_picture_upload(request):
    '''
    Upload a picture for a given event.
    '''
    response = {'accepted': False}
    error = _validate_request(request)
    if error:
        return error
    if 'event' not in request.POST:
        response['error'] = 'MISSING INFO'
        return JsonResponse(response)

    # Ensure that the given event exists
    event_id = request.POST['event']
    event = Event.objects.get(pk=event_id)
    if not event:
        response['error'] = 'Invalid event'
        return JsonResponse(response)
    if event.admin.user.id != request.user.id:
        # Make sure that user is the event's admin
        response['error'] = 'Invalid permissions'
        return JsonResponse(response)
    if not request.FILES or not request.FILES['picture']:
        response['error'] = 'No picture attached'
        return JsonResponse(response)

    # Update the event's picture
    pictures.upload_event(event, request.FILES['picture'])
    response['accepted'] = True
    return JsonResponse(response)


@csrf_exempt
def event_picture_delete(request):
    '''
    Delete the given event's picture if it exists.
    '''
    response = {'accepted': False}
    error = _validate_request(request)
    if error:
        return error
    if 'event' not in request.POST:
        response['error'] = 'MISSING INFO'
        return JsonResponse(response)

    # Ensure that the given event exists
    event_id = request.POST['event']
    event = Event.objects.get(pk=event_id)
    if not event:
        response['error'] = 'Invalid event'
        return JsonResponse(response)
    if event.admin.user.id != request.user.id:
        # Make sure that user is the event's admin
        response['error'] = 'Invalid permissions'
        return JsonResponse(response)

    # Delete the event's picture
    pictures.delete_event(event)
    response['accepted'] = True
    return JsonResponse(response)
