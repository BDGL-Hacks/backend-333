from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


# Additional information about users that is not needed at registration
class User_Profile(models.Model):
    # Should be set to "M" or "F"
    gender = models.CharField(max_length=1, null=True)

    birthday = models.DateTimeField(null=True)

    # Events for which the user is the administrator
    event_admin_list = None

    # Events the user has been invited to
    event_invite_list = None

    # Events the user is attending
    event_attending_list = None

    # Active groups the users is currently a part of
    groups_current = None

    # Inactive groups the user was a part of
    groups_past = None

    # Need to figure this out
    profile_picture = None


class Person(models.Model):
    # Built-in Django user
    # See https://docs.djangoproject.com/en/1.7/ref/contrib/auth/
    # for information about models.User
    user = models.OneToOneField(User)

    # Additional information about the user that is not needed at registration
    profile = models.ForeignKey(User_Profile)

    def __str__(self):
        return self.user.username


class Event(models.Model):
    date_created = models.DateTimeField('date published', default=datetime.now)
    created_by = models.ForeignKey(Person, related_name='event_creator')
    is_active = None

    # Admin is in charge of event and can post in Event message board
    admin = models.ForeignKey(Person)
    title = None
    public = None
    location = None
    time = None
    age_restrictions = None
    price = None
    description = None

    invite_list = None
    attending = None

    # TODO later
    category = None
    picture = None


class Group(models.Model):
    date_created = models.DateTimeField('date published', default=datetime.now)
    created_by = models.ForeignKey(Person, related_name='group_creator')

    # People in the group
    group_members = models.ManyToManyField(Person)

    '''
    Night/itinerary
    '''
    events = models.ManyToManyField(Event)

    is_active = None

    # Pusher
    chat_channel = None

    # Maybe
    picture = None
