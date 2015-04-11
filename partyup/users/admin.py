from django.contrib import admin
from .models import User_Profile, Event, Group, Message, Channel

admin.site.register(User_Profile)
admin.site.register(Event)
admin.site.register(Group)
admin.site.register(Channel)
admin.site.register(Message)
