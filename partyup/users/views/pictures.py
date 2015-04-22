'''
This file contains helper functions for uploading and deleting pictures and
performing other operations that involve the AWS S3 bucket.
'''
from base64 import b64encode
from boto.s3.connection import S3Connection
from boto.s3.key import Key
# from django.conf import settings
from hashlib import md5
from users.models import User_Profile, Event, Group
import os


def _save_local_picture(f, name):
    '''
    Saves the given file, f, locally with name, "name".
    '''
    safe_name = name.strip('/').strip('\\')
    path = os.path.join(os.getcwd(), 'users/views/temp_pictures', safe_name)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def _delete_local_picture(name):
    '''
    Locally remove the given picture if it exists.
    '''
    safe_name = name.strip('/').strip('\\')
    path = os.path.join(os.getcwd(), 'users/views/temp_pictures', safe_name)
    os.remove(path)


def _generate_key(key):
    '''
    Returns the unique key generated from given key.
    '''
    return b64encode(md5(key).digest())


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
    unique_key = _generate_key(key)

    # Send the picture along to AWS
    key_name = os.path.join(picture_type, unique_key)
    k = bucket.new_key(key_name)
    k.set_contents_from_filename(
        os.path.join('users/views/temp_pictures', picture))
    return key_name


def _delete_picture(key):
    '''
    Deletes the file associated with the given unique key.
    '''
    if not key:
        return

    conn = S3Connection()
    bucket = conn.get_bucket('partyup')
    k = Key(bucket)
    k.key = key
    k.delete()


def upload_event(event, multipart_file):
    '''
    Takes an Event object and the file that was included in a multipart post
    request.
    '''
    picture_name = str(event.id) + '.jpg'
    _save_local_picture(multipart_file, picture_name)
    key = _upload_picture('events', str(event.id), picture_name)
    _delete_local_picture(picture_name)
    event.picture = key
    event.save()


def delete_event(event):
    '''
    Delete the picture for the given Event object.
    '''
    _delete_picture(event.picture)
    event.picture = None
    event.save()


def upload_user(user_profile, multipart_file):
    '''
    Takes a User_Profile object and the file that was included in a multipart
    post request.
    '''
    picture_name = str(user_profile.id) + '.jpg'
    _save_local_picture(multipart_file, picture_name)
    key = _upload_picture('users', str(user_profile.id), picture_name)
    _delete_local_picture(picture_name)
    user_profile.picture = key
    user_profile.save()


def delete_user(user_profile):
    '''
    Delete the picture for the given User_Profile object.
    '''
    _delete_picture(user_profile.picture)
    user_profile.picture = None
    user_profile.save()


def upload_group(group, multipart_file):
    '''
    Takes a Group object and the file that was included in a multipart post
    request.
    '''
    picture_name = str(group.id) + '.jpg'
    _save_local_picture(multipart_file, picture_name)
    key = _upload_picture('groups', str(group.id), picture_name)
    _delete_local_picture(picture_name)
    group.picture = key
    group.save()


def delete_group(group):
    '''
    Delete the picture for the given Group object.
    '''
    _delete_picture(group.picture)
    group.picture = None
    group.save()
