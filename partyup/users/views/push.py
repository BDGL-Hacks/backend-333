from push_notifications.models import APNSDevice
from django.http import JsonResponse
from django.db import IntegrityError


def add_device(deviceID, user):
    '''
    Add a phone device to a user.
    If user has a phone device it will update
    the id.
    '''
    print("trying to add device")
    print("registration_id: " + str(deviceID))
    # delete an old device with the id
    oldDevice = APNSDevice.objects.filter(registration_id=deviceID)
    if oldDevice:
        print ("Removing old device")
        oldDevice = oldDevice[0]
        print (oldDevice)
        oldUser = oldDevice.user_profile_set.all()[0]
        oldUser.device = None
        oldUser.save()
        user.device = oldDevice
        user.save()
        return

    if not user.device:
        # Create the device
        device = APNSDevice(name=user.user.email, registration_id=deviceID)
        device.save()

            # Add the device to the user
        user.device = device
        user.save()
    else:
        if user.device.registration_id != deviceID:
            user.device.registration_id = deviceID
            user.device.save()


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
    if not device:
        return
    if not badge and extra:
        device.send_message(message, extra=extra)
    if badge and not extra:
        device.send_message(message, badge=badge)
    if badge and extra:
        device.send_message(message, extra=extra, badge=badge)
    if not badge and not extra:
        device.send_message(message)
