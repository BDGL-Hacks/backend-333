from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import Event, User_Profile, Group, User_Group_info
from datetime import date, datetime
from push import send_group_message


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
def respond_invite(request):
    '''
    A view to respond to an invite
    POST request needs
       obj_type = {event, group, ping}
       accept   = {true, false}
    '''
    error = _validate_request(request)
    if error:
        return error

    # Grabs the post data
    data = request.POST
    user = request.user.user_profile
    response = {}
    obj_type = data.get("obj_type", "")
    accept = data.get("accept", "")
    obj_id = data.get("obj_id", "")

    # Checks for missing info
    if not obj_type or not obj_id or not accept:
        response['error'] = 'Missing information'
        response['accepted'] = False
        return JsonResponse(response)

    # Responds to an event invite
    if obj_type == 'event':
        event = user.event_invite_list.filter(id=obj_id)
        if not event:
            response['error'] = 'You have already responded to this request'
            response['accepted'] = False
            return JsonResponse(response)
        event = event[0]
        # Remove user/event from invite lists
        user.event_invite_list.remove(event)
        event.invite_list.remove(user)
        # Accept on both sides
        if accept == 'True' or accept == 'true':
            user.event_attending_list.add(event)
            event.attending_list.add(user)
        # Save both event/user
        event.save()
        user.save()

    # Responds to a group invite
    elif obj_type == 'group':
        group = user.groups_invite_list.filter(id=obj_id)
        if not group:
            response['error'] = 'You have already responded to this request'
            response['accepted'] = False
            return JsonResponse(response)
        group = group[0]
        # Remove user/group from invite lists
        user.groups_invite_list.remove(group)
        group.invited_members.remove(user)
        # Accept on both sides
        if accept == 'True' or accept == 'true':
            user.groups_current.add(group)
            # Accept group with UGI
            ugi = User_Group_info(user_profile=user, group=group, status=group.current_event)
            ugi.save()
        # save both group/user
        group.save()
        user.save()

    # Responds to an incorrect invite
    else:
        response['error'] = 'Wrong object type'
        response['accepted'] = False
        return JsonResponse(response)

    # Invite proccessed correctly
    response['accepted'] = True
    return JsonResponse(response)


@csrf_exempt
def group_invite_view(request):
    '''
    The view to invite users to a group
    '''
    error = _validate_request(request)
    if error:
        return error
    info = {
        'data': request.POST,
        'user': request.user.user_profile
    }
    return JsonResponse(group_invite(info))


def group_invite(info):
    '''
    Helper method that invites the list of users to a group.
    Info should be a dictionary with
    data = a dictionary with group, invitee
    (invitee should be comma separated ids of User_Profiles)
    (group should be an group id)
    and
    user = the user_profile that sent the request
    '''
    data = info['data']
    user = info['user']
    response = {}

    groupID = data.get("group", '')
    inviteeIDs = data.get('invitee', '')
    try:
        groupID = int(groupID)
    except ValueError:
        response['error'] = 'Please provide Group/Invitee IDs'
        response['accepted'] = False
        return response

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

    # Send invites to everyone
    if inviteeIDs:
        invitees = inviteeIDs.split(',')
    # have an impossible id if no invites
    else:
        invitees = [-1]
    inviteeSet = User_Profile.objects.filter(id__in=invitees)
    for invitee in inviteeSet:
        # Checks to see if an invitee already exists in the group
        if not group.group_members.filter(id=invitee.id).exists():
            invitee.groups_invite_list.add(group)
            invitee.save()
            group.invited_members.add(invitee)
        else:
            print ("Tried to invite someone that is attending group")
    group.save()

    # Send push notifications to everyone
    message = "Group invite to: \"" + group.title + "\""
    extra = {
        'type': 'group-invite',
        'content': {
            'id': group.id,
        },
    }
    send_group_message(inviteeSet, message, extra=extra)

    # return successfully
    response['accepted'] = True
    return response


def event_invite(info):
    '''
    Helper method that invites the list of users to an event.
    Info should be a dictionary with
    data = a dictionary with event, invitee
    (invitee should be comma separated ids of User_Profiles)
    (event should be an event id)
    and
    user = the user_profile that sent the request
    '''
    data = info['data']
    user = info['user']
    response = {}

    # Check for proper POST data
    eventID = data.get("event", '')
    inviteeIDs = data.get('invitee', '')

    try:
        eventID = int(eventID)
    except ValueError:
        response['error'] = 'Please provide Event/Invitee IDs'
        response['accepted'] = False
        return response

    # Check that event exists
    event = Event.objects.filter(id=eventID)
    if not event:
        response['error'] = 'The event requested does not exist'
        response['accepted'] = False
        return response
    event = event[0]

    # Check event permission
    if event.public:
        if not event.attending_list.filter(id=user.id):
            response['error'] = 'You do not have permission to add to this event'
            response['accepted'] = False
            return response
    else:
        if not event.admin.id == user.id:
            response['error'] = 'You do not have permission to add to this event'
            response['accepted'] = False
            return response

    # Send invites to everyone
    if inviteeIDs:
        invitees = inviteeIDs.split(',')
    # if no invites then have an impossible id
    else:
        invitees = [-1]

    inviteeSet = User_Profile.objects.filter(id__in=invitees)
    for invitee in inviteeSet:
        # Checks to see if an invitee already exists in the event
        if not event.attending_list.filter(id=invitee.id).exists():
            invitee.event_invite_list.add(event)
            invitee.save()
            event.invite_list.add(invitee)
        else:
            print ("There is someone already invited to this event")
    event.save()

    # Send push notifications to everyone
    message = "Event invite to: \"" + event.title + "\""
    extra = {
        'type': 'event-invite',
        'content': {
            'id': event.id,
        }
    }
    send_group_message(inviteeSet, message, extra=extra)

    # return successfully
    response['accepted'] = True
    return response


@csrf_exempt
def event_invite_view(request):
    '''
    The view to invite users to an event
    '''
    error = _validate_request(request)
    if error:
        return error
    info = {
        'data': request.POST,
        'user': request.user.user_profile,
    }
    return JsonResponse(event_invite(info))
