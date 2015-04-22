'''
This file contains helper functions for uploading and deleting pictures and
performing other operations that involve the AWS S3 bucket.
'''
from base64 import b64encode
from boto.s3.connection import S3Connection
from boto.s3.key import Key
# from django.conf import settings
from django.contrib.auth import login, authenticate
from hashlib import md5
from users.models import User_Profile, Event, Group
import os


def _validate_picture_request(request):
    '''
    Take a django request and check whether it contains the proper
    information for a picture upload.

    Raise an exception if request is invalid. Return None otherwise.
    '''
    # Check that the request is a POST
    if request.method != 'POST':
        message = 'NOT A POST REQUEST'
        raise AssertionError(message)
    # Check that the user is logged in
    if not request.user.is_authenticated():
        message = 'User is not logged in'
        raise AssertionError(message)
    if not request.FILES or not request.FILES['picture']:
        message = 'No picture attached'
        raise AssertionError(message)
    return None


def _save_picture(f, name):
    '''
    Saves the given file, f, locally with name, "name".
    '''
    safe_name = name.strip('/').strip('\\')
    path = os.path.join(os.getcwd(), 'users/views/temp_pictures', safe_name)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def _delete_picture(name):
    '''
    Locally remove the given picture if it exists.
    '''
    safe_name = name.strip('/').strip('\\')
    path = os.path.join(os.getcwd(), 'users/views/temp_pictures', safe_name)
    os.remove(path)


def _upload_picture(picture_type, key, picture):
    '''
    Upload the given picture (stored locally) to the AWS S3 bucket. The
    folder to which the picture should be uploaded is specified by the
    picture_type argument. Raises a ValueError when input is invalid.
    Returns the picture's key on success.

    Note that this function will overwrite existing pictures with the same
    key.
    '''
    # Validate picture_type
    if picture_type != 'events' and \
       picture_type != 'groups' and \
       picture_type != 'users':
        raise ValueError('Invalid picture_type must be "events", \
                         "groups", or "users".')

    # Connect to the S3 bucket
    conn = S3Connection()
    bucket = conn.get_bucket('partyup')

    # Hash for uniqueness
    unique_key = b64encode(md5(key).digest())

    # Send the picture along to AWS
    key_name = os.path.join(picture_type, unique_key)
    k = bucket.new_key(key_name)
    k.set_contents_from_filename(
        os.path.join('users/views/temp_pictures', picture))
    return key_name


def upload_event_picture(request):
    '''
    Takes a django request that includes a picture for an event.
    '''
    _validate_picture_request(request)
    if not request.POST['event']:
        # Additional validation
        raise AssertionError('No event specified')

    event_id = request.POST['event']
    event = Event.objects.get(pk=event_id)
    if not event:
        raise AssertionError('Invalid event')

    picture = request.FILES['picture']
    picture_name = str(event.id) + '.jpg'
    _save_picture(picture, picture_name)
    key = _upload_picture('events', str(event.id), picture_name)
    event.picture = key
    event.save()
    _delete_picture(picture_name)
