'''
This file contains helper functions for uploading and deleting pictures and
performing other operations that involve the AWS S3 bucket.
'''
from boto.s3.connection import S3Connection
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from users.models import User_Profile


def _upload_picture(picture_type, picture):
    '''
    Upload the given picture to the AWS S3 bucket. The folder to which the
    picture should be uploaded is specified by the picture_type argument.
    Returns True on success and False otherwise.
    '''
    # Validate picture_type
    if picture_type == 'events' or \
       picture_type == 'groups' or \
       picture_type == 'users':
        folder = picture_type
    else:
        return False

    # Connect to the S3 bucket
    conn = S3Connection()
    my_bucket = conn.get_bucket('partyup')
    print my_bucket.list()

if __name__ == '__main__':
    _upload_picture('events', None)
