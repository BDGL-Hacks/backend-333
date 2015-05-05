from django.contrib import admin
from .models import User_Profile, Event, Group, Message, Channel, User_Group_info, Ping

admin.site.register(User_Profile)
admin.site.register(Event)
admin.site.register(Group)
admin.site.register(Channel)
admin.site.register(Message)
admin.site.register(User_Group_info)
admin.site.register(Ping)
