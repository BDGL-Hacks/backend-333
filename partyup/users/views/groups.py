from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from invites import group_invite
from push import send_group_message
from users.models import Event, Group, Channel, User_Group_info
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
def group_create(request):
    '''
    Creates a group.
    Mandatory Data
       event_ids (comma seperated ids)
       invite_list (comma seperated ids)
    '''
    response = {}
    # Verify that we are posting data
    if request.method != 'POST':
        response['error'] = 'NOT A POST REQUEST'
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
    event_ids = request.POST.get('event_ids', '')
    invite_list = request.POST.get('invite_list', '')

    group_name = request.POST.get('title', '')

    # Check for mandatory data
    if not event_ids or not group_name:
        response['error'] = 'MISSING INFO'
        response['accepted'] = False
        return JsonResponse(response)

    # Split the ids
    event_ids = event_ids.split(',')
    # Create and save the group
    group = Group(created_by=user, title=group_name)
    group.save()

    # Make the chat channel with the group id
    channel_name = "GroupChat" + str(group.id)
    group.chat_channel = channel_name
    channel = Channel(name=channel_name, group=group)
    channel.save()

    # add all events to the group
    events = Event.objects.filter(id__in=event_ids)
    for event in events:
        group.events.add(event)

    # make the current event the most recent
    group.current_event = events.earliest('time')

    # add user to be attending their own group
    # uses User_Group_info
    user.groups_current.add(group)
    ugi = User_Group_info(user_profile=user, group=group, status=group.current_event)
    ugi.save()
    user.save()

    # invite all of the users
    info = {
        'data': {
            'group': group.id,
            'invitee': invite_list,
        },
        'user': user
    }
    invite_response = group_invite(info)
    if not invite_response['accepted']:
        return JsonResponse(invite_response)

    group.save()
    response['accepted'] = True
    return JsonResponse(response)


@csrf_exempt
def group_getid(request):
    '''
    gets a single group by its id.
    The user must be a part of the group for this/
    '''
    error = _validate_request(request)
    if error:
        return error

    response = {}
    data = request.POST
    user = request.user.user_profile
    groupid = data.get('id', '')
    if not groupid:
        response['error'] = 'MISSING INFO'
        response['accepted'] = False
        return JsonResponse(response)

    # Get the group Object
    group = Group.objects.filter(id=groupid)
    if not group:
        response['error'] = 'INCORRECT ID'
        response['accepted'] = False
        return JsonResponse(response)
    group = group[0]
    # Check for Permission
    if not group.group_members.filter(id=user.id):
        response['error'] = 'NEED PERMISSION FOR GROUP'
        response['accepted'] = False
        return JsonResponse(response)

    # Return sucessfully
    response['accepted'] = True
    response['group'] = group.to_dict()
    return JsonResponse(response)


@csrf_exempt
def group_get(request):
    '''
    Get all relevant groups
    Can get attending, created, or invited groups
    Groups chosen by 'type' POST data
    '''
    error = _validate_request(request)
    if error:
        return error

    response = {}
    print request.user
    print request.user.email
    user = request.user.user_profile
    for t in request.POST.getlist('type'):
        if t == 'attending':
            result = user.groups_current.all()
        elif t == 'created':
            result = Group.objects.all().filter(created_by=user)
        elif t == 'invited':
            result = user.groups_invite_list.all()
        else:
            return JsonResponse({'accepted': False, 'error': 'Invalid type'})
        groups = [group.to_dict() for group in result]
        response[t] = groups

    response['accepted'] = True
    return JsonResponse(response)


@csrf_exempt
def group_add_events(request):
    '''
    Add an event to a group's itinerary. Anyone in the group can do this.
    '''
    response = {'accepted': False}
    error = _validate_request(request)
    if error:
        return error

    user = request.user.user_profile

    groupID = request.POST.get('group', '')
    eventIDs = request.POST.get('eventIDs', '')

    if not eventIDs or not groupID:
        response['error'] = 'MISSING INFO'
        return JsonResponse(response)

    # Check for group's existence
    group = Group.objects.filter(id=groupID)
    if not group:
        response['error'] = 'The group requested does not exist'
        response['accepted'] = False
        return response
    group = group[0]

    # Check for proper permission
    if not group.group_members.filter(id=user.id):
        response['error'] = 'You do not have permission to add to this group'
        response['accepted'] = False
        return response

    event_ids = eventIDs.split(',')
    # grab events and add them to the group
    events = Event.objects.filter(id__in=event_ids)
    for event in events:
        group.events.add(event)

    # change the group's current events
    group.current_event = group.events.earliest('time')
    group.save()

    # return successfully
    response['accepted'] = True
    return JsonResponse(response)


@csrf_exempt
def group_change_currentevent(request):
    '''
    Set the current event for a group. Can only be done by the admin.
    '''
    response = {'accepted': False}
    error = _validate_request(request)
    if error:
        return error

    user = request.user.user_profile
    groupID = request.POST.get('group', '')
    eventID = request.POST.get('event', '')
    if not eventID or not groupID:
        response['error'] = 'MISSING INFO'
        return JsonResponse(response)

    # Check for group's existence
    group = Group.objects.filter(id=groupID)
    if not group:
        response['error'] = 'The group requested does not exist'
        return JsonResponse(response)
    group = group[0]

    # Check that the user is in the group
    if not group.group_members.filter(id=user.id):
        response['error'] = 'You do are not in the group'
        return JsonResponse(response)

    # Make sure the user is the admin.
    if group.created_by != user:
        response['error'] = 'Invalid permissions'
        return JsonResponse(response)

    # Check that the event is in the group itinerary
    event = group.events.filter(id=eventID)
    if not event:
        response['error'] = 'The event is not in the group itinerary'
        response['accepted'] = False
        return JsonResponse(response)
    event = event[0]

    # Add the event as current
    group.current_event = event
    group.save()

    # Reset everyone's status/indicators
    members_info = User_Group_info.objects.filter(group=group)
    for member in members_info:
        if member.user_profile == user:
            member.status = event
        member.indicator = 1
        member.save()

    # TODO send push notification/alert
    # Send notifications to all but the person admin
    users = group.group_members.all().exclude(user=user.user)
    message = group.title + ': Going to ' + group.current_event.title
    extra = {
        'type': 'location-change',
        'content': {
            'group': group.id,
            'new_location': group.current_event.to_dict_sparse(),
        },
    }
    send_group_message(users, message, extra=extra)

    # return successfully
    response['accepted'] = True
    return JsonResponse(response)


@csrf_exempt
def group_update_status(request):
    '''
    Change a user's current location, which will update the user's indicator
    and other settings accordingly.
    '''
    response = {'accepted': False}
    error = _validate_request(request)
    if error:
        return error

    user = request.user.user_profile
    groupID = request.POST.get('group', '')
    eventID = request.POST.get('event', '')

    if not groupID or not eventID:
        response['error'] = 'MISSING INFO'
        return JsonResponse(response)

    # Check input
    group = Group.objects.get(pk=groupID)
    user_info = User_Group_info.objects.filter(user_profile__id=user.id, group__id=groupID)
    if not user_info:
        response['error'] = 'Cannot find user.'
        return JsonResponse(response)
    event = Event.objects.get(pk=eventID)
    if not event:
        response['error'] = 'Invalid event.'
        return JsonResponse(response)
    if not Group.objects.get(pk=groupID).events.all().filter(id=eventID):
        response['error'] = 'Event not in itinerary.'
        return JsonResponse(response)

    # update status
    user_info = user_info[0]
    user_info.status = event
    if event != group.current_event:
        # Yellow/neutral indicator
        user_info.indicator = 1
    else:
        # Green/okay indicator
        user_info.indicator = 0
    user_info.save()

    # return successfully
    response['accepted'] = True
    return JsonResponse(response)


@csrf_exempt
def group_picture_upload(request):
    '''
    Upload a picture for a given group.
    '''
    response = {'accepted': False}
    error = _validate_request(request)
    if error:
        return error
    if 'group' not in request.POST:
        response['error'] = 'MISSING INFO'
        return JsonResponse(response)

    # Check whether given group exists
    group_id = request.POST['group']
    group = Group.objects.get(pk=group_id)
    if not group:
        response['error'] = 'Invalid group'
        return JsonResponse(response)
    if request.user not in [u.user for u in group.group_members.all()]:
        response['error'] = 'Invalid permissions'
        return JsonResponse(response)
    if not request.FILES or not request.FILES['picture']:
        response['error'] = 'No picture attached'
        return JsonResponse(response)

    # Upload the picture
    pictures.upload_group(group, request.FILES['picture'])
    response['accepted'] = True
    return JsonResponse(response)


@csrf_exempt
def group_picture_delete(request):
    '''
    Delete the given group's picture if it exists.
    '''
    response = {'accepted': False}
    error = _validate_request(request)
    if error:
        return error
    if 'group' not in request.POST:
        response['error'] = 'MISSING INFO'
        return JsonResponse(response)

    # Check whether given group exists
    group_id = request.POST['group']
    group = Group.objects.get(pk=group_id)
    if not group:
        response['error'] = 'Invalid group'
        return JsonResponse(response)
    if request.user not in [u.user for u in group.group_members.all()]:
        response['error'] = 'Invalid permissions'
        return JsonResponse(response)

    # Delete the picture
    pictures.delete_group(group)
    response['accepted'] = True
    return JsonResponse(response)
