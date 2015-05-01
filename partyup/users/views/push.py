from push_notifications.models import APNSDevice
from django.http import JsonResponse
from django.db import IntegrityError

def add_device(deviceID, user):
    print ("START")
    try:
        if not user.device: 
            # Create the device
            device = APNSDevice(name=user.user.email, registration_id=deviceID)
            device.save()
            print ("ADDING DEVICE")

            # Add the device to the user
            user.device = device
            user.save()
        else:
            user.device.registration_id=deviceID
            user.device.save()
    except IntegrityError:
        return JsonResponse({'error': "Duplicate Device ID",
            'accepted': False})

def send_group_message(users, message, badge=None, extra=None):
    devices = APNSDevice.objects.filter(id__in=users.values('device_id'))
    for device in devices:
        device.send_message(message,badge=badge,extra=extra)

def send_message(user, message, badge=None, extra=None):
    device = user.device
    if not badge and extra:
        device.send_message(message,extra=extra)
    if badge and not extra:
        device.send_message(message,badge=badge)
    if badge and extra:
        device.send_message(message,extra=extra, badge=badge)
    if not badge and not extra:
        device.send_message(message)



