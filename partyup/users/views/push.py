from push_notifications.models import APNSDevice
from django.http import JsonResponse
from django.db import IntegrityError


def add_device(deviceID, user):
    '''
    Add a phone device to a user.
    If user has a phone device it will update
    the id.
    '''
    try:
        if not user.device:
            # Create the device
            device = APNSDevice(name=user.user.email, registration_id=deviceID)
            device.save()

            # Add the device to the user
            user.device = device
            user.save()
        else:
            user.device.registration_id = deviceID
            user.device.save()
    # Check if the id exists for another user
    except IntegrityError:
        return JsonResponse({'error': "Duplicate Device ID",
                            'accepted': False})


def send_group_message(users, message, badge=None, extra=None):
    '''
    Send a message to a a Query_Set of User_Profiles
    '''
    devices = APNSDevice.objects.filter(id__in=users.values('device_id'))

    for device in devices:
        if not badge and extra:
            device.send_message(message, extra=extra)
        if badge and not extra:
            device.send_message(message, badge=badge)
        if badge and extra:
            device.send_message(message, extra=extra, badge=badge)
        if not badge and not extra:
            device.send_message(message)


def send_message(user, message, badge=None, extra=None):
    '''
    Sends a message to a single user
    '''
    device = user.device
    if not badge and extra:
        device.send_message(message, extra=extra)
    if badge and not extra:
        device.send_message(message, badge=badge)
    if badge and extra:
        device.send_message(message, extra=extra, badge=badge)
    if not badge and not extra:
        device.send_message(message)
