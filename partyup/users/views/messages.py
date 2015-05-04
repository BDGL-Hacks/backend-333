from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from users.models import User_Profile, Event, Group, Message
from keys.pusherAPI import createPusher
from push import send_group_message

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
    '''
    Takes a post value of
       groupid - the group for messages
       messageID - the last message received
    The method gets the last ten messages before messageID
    If no messageID is given it gives the most recent 10 messages
    '''
    error = _validate_request(request)
    if error:
        return error

    # gets the POST data
    response = {}
    data = request.POST
    user = request.user.user_profile
    groupid = data.get('groupid', '')
    messageID = int(data.get('messageid', '-1'))
    # checks POST data
    if not groupid:
        response['error'] = 'MISSING INFO'
        response['accepted'] = False
        return JsonResponse(response)

    # gets the group
    group = Group.objects.filter(id=groupid)
    if not group:
        response['error'] = 'INCORRECT ID'
        response['accepted'] = False
        return JsonResponse(response)
    group = group[0]
    # checks for permission
    if not group.group_members.filter(id=user.id):
        response['error'] = 'NEED PERMISSION FOR GROUP'
        response['accepted'] = False
        return JsonResponse(response)

    # grabs the channel
    channel = group.channel_set.all()[0]
    # if no messageID then use the highest (most recent) messages
    if messageID < 0:
        messageID = channel.num_messages
    messages = []
    messagesObj = Message.objects.filter(channel=channel)

    # index is the last 10 messages from messageID
    index = messageID - 10
    # edge case for when returning the first few messages
    if index < 0:
        index = 0
    messagesObj = messagesObj[index:messageID]

    # Change each message object to jSON
    for message in messagesObj:
        messages.append({
            'id': message.number,
            'message': message.text,
            'owner': message.owner.to_dict(),
            'time': message.time_sent,
        })

    # Return successfully
    response = {
        'results': messages,
        'accepted': True,
        'userID': user.id,
    }
    return JsonResponse(response)


@csrf_exempt
def messages_post(request):
    '''
    Post a message to a certain group
    User must have group permission
    '''
    error = _validate_request(request)
    if error:
        return error

    # get POST data
    response = {}
    data = request.POST
    user = request.user.user_profile
    groupid = data.get('groupid', '')
    message = data.get('message', '')
    if not groupid or not message:
        response['error'] = 'MISSING INFO'
        response['accepted'] = False
        return JsonResponse(response)

    # get the group object
    group = Group.objects.filter(id=groupid)
    if not group:
        response['error'] = 'INCORRECT ID'
        response['accepted'] = False
        return JsonResponse(response)
    group = group[0]

    # check permissions
    if not group.group_members.filter(id=user.id):
        response['error'] = 'NEED PERMISSION FOR GROUP'
        response['accepted'] = False
        return JsonResponse(response)

    # get the channel, add to the number of messages
    channel = group.channel_set.all()[0]
    channel.num_messages += 1
    channel.save()

    # make the message object
    messageObj = Message(channel=channel, owner=user,
                         text=message, number=channel.num_messages)
    messageObj.save()

    messageData = {
        'type': 'message',
        'content': {
            'message': message,
            'owner': messageObj.owner.to_dict(),
            'time': str(messageObj.time_sent),
            'group': groupid,
        },
    }

    # send the message through PUSHER
    pusherAPI[channel.name].trigger('message', messageData)

    # send a push notification to the members of the group
    # exclude the user sending the messages
    users = group.group_members.exclude(id=user.id)
    message = user.user.first_name + ": " + message
    send_group_message(users, message, extra=messageData)

    # return successfully
    response['accepted'] = True
    return JsonResponse(response)
