from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from users.models import User_Profile, Event, Group, Message
from keys.pusherAPI import createPusher

pusherAPI = createPusher()

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
def messages_get(request):
    error = _validate_request(request)
    if error:
        return error

    response = {}
    data = request.POST
    user = request.user.user_profile

    groupid = data.get('groupid', '')
    messageID = int(data.get('messageid', '-1'))
    if not groupid:
        response['error'] = 'MISSING INFO'
        response['accepted'] = False
        return JsonResponse(response)
    
    group = Group.objects.filter(id=groupid)
    if not group:
        response['error'] = 'INCORRECT ID'
        response['accepted'] = False
        return JsonResponse(response)
    group = group[0]

    if not group.group_members.filter(id=user.id):
        response['error'] = 'NEED PERMISSION FOR GROUP'
        response['accepted'] = False
        return JsonResponse(response)

    channel = group.channel_set.all()[0]
    if messageID < 0:
        messageID = channel.num_messages
    messages = []
    messagesObj = Message.objects.filter(channel=channel)
    index = messageID - 10
    if index < 0:
        index = 0
    messagesObj = messagesObj[index:messageID - 1]
    for message in messagesObj:
        messages.append( {
            'id': message.number,
            'message': message.text,
        })
        response = {
            'messages':messages,
            'accepted':True,
        }
    return JsonResponse(response)

@csrf_exempt
def messages_post(request):
    error = _validate_request(request)
    if error:
        return error

    response = {}
    data = request.POST
    user = request.user.user_profile

    groupid = data.get('groupid', '')
    message = data.get('message', '')
    if not groupid or not message:
        response['error'] = 'MISSING INFO'
        response['accepted'] = False
        return JsonResponse(response)
    
    group = Group.objects.filter(id=groupid)
    if not group:
        response['error'] = 'INCORRECT ID'
        response['accepted'] = False
        return JsonResponse(response)
    group = group[0]

    if not group.group_members.filter(id=user.id):
        response['error'] = 'NEED PERMISSION FOR GROUP'
        response['accepted'] = False
        return JsonResponse(response)

    channel = group.channel_set.all()[0]
    channel.num_messages += 1
    channel.save()
    messageObj = Message(channel=channel, owner=user, text=message, number=channel.num_messages)
    messageObj.save()
    pusherAPI[channel.name].trigger('message',{'message': message})
    response['accepted'] = True 
    return JsonResponse(response)
