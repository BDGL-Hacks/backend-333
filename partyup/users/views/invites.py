from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import Event, User_Profile, Group
from datetime import date, datetime

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
    error = _validate_request(request)
    if error:
        return error

    data = request.POST
    user = request.user.user_profile
    response = {}

    obj_type = data.get("obj_type", "")
    accept = data.get("accept", "")
    obj_id = data.get("obj_id", "")

    if not obj_type or not obj_id or not accept:
        response['error'] = 'Missing information'
        response['accepted'] = False
        return JsonResponse(response)

    
    if obj_type == 'event':
        event = user.event_invite_list.filter(id=obj_id)    
        if not event:
            response['error'] = 'You have already responded to this request'
            response['accepted'] = False
            return JsonResponse(response)
            
        event = event[0]
        user.event_invite_list.remove(event)
        if accept == 'True' or accept == 'true':
            user.event_attending_list.add(event)
        user.save()
    elif obj_type == 'group':
        group = user.groups_invite_list.filter(id=obj_id)
        if not group:
            response['error'] = 'You have already responded to this request'
            response['accepted'] = False
            return JsonResponse(response)

        group = group[0]
        user.groups_invite_list.remove(group)
        if accept == 'True' or accept == 'true':
            user.groups_current.add(group)
        user.save()
    else:
        response['error'] = 'Wrong object type'
        response['accepted'] = False
        return JsonResponse(response)

    response['accepted'] = True
    return JsonResponse(response)
        
@csrf_exempt
def group_invite(request):
    error = _validate_request(request)
    if error:
        return error

    data = request.POST
    user = request.user.user_profile
    response = {}

    groupID = data.get("group", '')
    inviteeIDs = data.get('invitee', '')
    try:
        groupID = int(groupID)
    except ValueError:
        response['error'] = 'Please provide Group/Invitee IDs'
        response['accepted'] = False
        return JsonResponse(response)

    group = Group.objects.filter(id=groupID)
    if not group:
        response['error'] = 'The group requested does not exist'
        response['accepted'] = False
        return JsonResponse(response)
    group = group[0]
    if not group.group_members.filter(id=user.id):
        response['error'] = 'You do not have permission to add to this group'
        response['accepted'] = False
        return JsonResponse(response)

    invitees = inviteeIDs.split(',')
    for i in invitees:
        invitee = User_Profile.objects.filter(id=i)
        if not invitee:
            response['error'] = 'The user requested does not exist'
            response['accepted'] = False
            return JsonResponse(response)

        invitee = invitee[0]
        # TODO: send push notifications for the person
        invitee.groups_invite_list.add(group)
        invitee.save()
        group.invited_members.add(invitee)
    group.save()

    response['accepted'] = True
    return JsonResponse(response)
    
@csrf_exempt
def event_invite(request):
    error = _validate_request(request)
    if error:
        return error

    data = request.POST
    user = request.user.user_profile
    response = {}

    eventID = data.get("event", '')
    inviteeIDs = data.get('invitee', '')
    try:
        eventID = int(eventID)
    except ValueError:
        response['error'] = 'Please provide Event/Invitee IDs'
        response['accepted'] = False
        return JsonResponse(response)

    event = Event.objects.filter(id=eventID)
    if not event:
        response['error'] = 'The event requested does not exist'
        response['accepted'] = False
        return JsonResponse(response)
    event = event[0]
    if event.public:
        if not event.attending_list.filter(id=user.id):
            response['error'] = 'You do not have permission to add to this event'
            response['accepted'] = False
            return JsonResponse(response)
    else:
        if not event.admin.id == user.id:
            response['error'] = 'You do not have permission to add to this event'
            response['accepted'] = False
            return JsonResponse(response)
            
    invitees = inviteeIDs.split(',')
    for i in invitees:
        invitee = User_Profile.objects.filter(id=i)
        if not invitee:
            response['error'] = 'The user requested does not exist'
            response['accepted'] = False
            return JsonResponse(response)

        invitee = invitee[0]
        # TODO: send push notifications for the person
        invitee.event_invite_list.add(event)
        invitee.save()
        event.invite_list.add(invitee)
    event.save()

    response['accepted'] = True
    return JsonResponse(response)
        
