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

