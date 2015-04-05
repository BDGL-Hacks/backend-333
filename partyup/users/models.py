from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


# Additional information about users that is not needed at registration
class User_Profile(models.Model):
    # Built-in Django user
    # See https://docs.djangoproject.com/en/1.7/ref/contrib/auth/
    # for information about models.User
    user = models.OneToOneField(User, null=True)
    # Should be set to "M" or "F"
    gender = models.CharField(max_length=1, null=True)

    birthday = models.DateTimeField(null=True)

    # Events for which the user is the administrator
    event_admin_list = models.ManyToManyField('Event', related_name='event_admin_list')

    # Events the user has been invited to
    event_invite_list = models.ManyToManyField('Event', related_name='event_invite_list')

    # Events the user is attending
    event_attending_list = models.ManyToManyField('Event', related_name='event_attending_list')

    # Active groups the users is currently a part of
    groups_current = models.ManyToManyField('Group', related_name='groups_current')

    # Inactive groups the user was a part of
    groups_past = models.ManyToManyField('Group', related_name='groups_past')

    # Need to figure this out
    profile_picture = None

    def __str__(self):
        return self.user.username




class Event(models.Model):
    date_created = models.DateTimeField('date published', default=datetime.now)
    created_by = models.ForeignKey(User_Profile, related_name='event_creator')
    is_active = None

    # Admin is in charge of event and can post in Event message board
    admin = models.ForeignKey(User_Profile)
    title = models.CharField(max_length=160, null=True)
    public = models.BooleanField(default=True)
    location = None
    time = models.DateTimeField('time of event')
    age_restrictions = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    description = models.CharField(max_length=300, null=True)

    invite_list = models.ManyToManyField(User_Profile, related_name='invite_list')
    attending_list = models.ManyToManyField(User_Profile, related_name='attending_list')

    # TODO later
    category = None
    picture = None
    def __str__(self):
        return self.title

class Group(models.Model):
    title = models.CharField(max_length=100)
    date_created = models.DateTimeField('date published', default=datetime.now)
    created_by = models.ForeignKey(User_Profile, related_name='group_creator')
    # People in the group
    group_members = models.ManyToManyField(User_Profile, related_name='group_members')
    invited_members = models.ManyToManyField(User_Profile, related_name='invited_members')
    '''
    Night/itinerary
    '''
    events = models.ManyToManyField(Event)

    is_active = models.BooleanField(default=True)

    # Pusher
    chat_channel = models.CharField(max_length=50, null=True)

    # Maybe
    picture = None
