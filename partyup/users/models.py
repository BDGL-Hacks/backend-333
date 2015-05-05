from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from push_notifications.models import APNSDevice


# Additional information about users that is not needed at registration
class User_Profile(models.Model):
    # Built-in Django user
    # See https://docs.djangoproject.com/en/1.7/ref/contrib/auth/
    # for information about models.User
    user = models.OneToOneField(User, null=True)
    # Should be set to "M" or "F"
    gender = models.CharField(max_length=1, null=True, blank=True)

    birthday = models.DateTimeField(null=True, blank=True)

    # Events for which the user is the administrator
    event_admin_list = models.ManyToManyField('Event', related_name='event_admin_list', blank=True)

    # Events the user has been invited to
    event_invite_list = models.ManyToManyField('Event', related_name='event_invite_list', blank=True)

    # Events the user is attending
    event_attending_list = models.ManyToManyField('Event', related_name='event_attending_list', blank=True)

    # Groups the user has been invited to
    groups_invite_list = models.ManyToManyField('Group', related_name='groups_invite_list', blank=True)

    # Active groups the users is currently a part of
    groups_current = models.ManyToManyField('Group', related_name='groups_current', blank=True)

    # Inactive groups the user was a part of
    groups_past = models.ManyToManyField('Group', related_name='groups_past', blank=True)

    # Profile picture
    picture = models.CharField(max_length=40, null=True, blank=True)

    # The device needed to send push notifications
    device = models.ForeignKey(APNSDevice, null=True, blank=True)

    def __str__(self):
        return str(self.user.email) + "\t" + str(self.id)

    # Return dictionary representation of an Event that can be sent to client
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'picture': self.picture
        }


class User_Group_info(models.Model):
    status = models.ForeignKey('Event')
    indicator = models.IntegerField(default=0)
    user_profile = models.ForeignKey('User_Profile')
    group = models.ForeignKey('Group')


class Event(models.Model):
    date_created = models.DateTimeField('date published', default=datetime.now)
    created_by = models.ForeignKey(User_Profile, related_name='event_creator')

    # TODO: This. Need to think about best way to update this field in practice
    is_active = None

    # Admin is in charge of event and can post in Event message board
    admin = models.ForeignKey(User_Profile)
    title = models.CharField(max_length=160, null=True)
    public = models.BooleanField(default=True)
    time = models.DateTimeField('time of event')
    age_restrictions = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    description = models.CharField(max_length=300, null=True)

    # Location information
    location_name = models.CharField(max_length=160)
    location_lat = None
    location_long = None

    invite_list = models.ManyToManyField(User_Profile, related_name='invite_list')
    attending_list = models.ManyToManyField(User_Profile, related_name='attending_list') 

    picture = models.CharField(max_length=40, null=True, blank=True)

    # TODO later
    category = None

    def __str__(self):
        return '%d %s' % (self.id, self.title)

    # Return dictionary representation of an Event that can be sent to client
    def to_dict(self):
        return {
            'date_created': str(self.date_created),
            'created_by': self.created_by,
            'admin': self.admin,
            'title': self.title,
            'public': self.public,
            'time': str(self.time),
            'age_restrictions': self.age_restrictions,
            'price': self.price,
            'description': self.description,
            'location_name': self.location_name,
            'invite_list': self.invite_list.all(),
            'attending_list': self.attending_list.all(),
            'id': self.id,
            'picture': self.picture,
        }

    def to_dict_sparse(self):
        return {
            'admin': self.admin.to_dict(),
            'title': self.title,
            'location_name': self.location_name,
            'time': str(self.time),
            'id': self.id,
        }


class Group(models.Model):
    title = models.CharField(max_length=100)
    date_created = models.DateTimeField('date published', default=datetime.now)
    created_by = models.ForeignKey(User_Profile, related_name='group_creator')
    # People in the group
    group_members = models.ManyToManyField(User_Profile, related_name='group_members', through='User_Group_info')
    invited_members = models.ManyToManyField(User_Profile, related_name='invited_members')
    '''
    Night/itinerary
    '''
    events = models.ManyToManyField(Event)
    current_event = models.ForeignKey(Event, related_name='current_event', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    picture = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return '%d %s' % (self.id, self.title)

    def to_dict(self):
        members = []
        for member in self.group_members.all():
            # Get standard User_Profile information as well as information
            # about the user's status in the group.
            info = member.to_dict()
            ugi = User_Group_info.objects.get(user_profile=member, group=self)
            info['group_status'] = {
                'status': ugi.status.to_dict_sparse(),
                'indicator': ugi.indicator,
            }
            members.append(info)
        events = []
        for event in self.events.all():
            print event
            events.append(event.to_dict_sparse())
        if self.current_event:
            current_event = self.current_event.to_dict_sparse()
        else:
            current_event = events[0]
        return {
            'id': self.id,
            'created_by': self.created_by.to_dict(),
            'title': self.title,
            'members': members,
            'events': events,
            'picture': self.picture,
            'current_event': current_event,
        }


class Channel(models.Model):
    name = models.CharField(max_length=50, null=True)
    group = models.ForeignKey(Group)
    num_messages = models.IntegerField(default=0)


class Message(models.Model):
    channel = models.ForeignKey(Channel)
    time_sent = models.DateTimeField('date published', default=datetime.now)
    owner = models.ForeignKey(User_Profile)
    text = models.CharField(max_length=160, null=True)
    number = models.IntegerField(default=0)
    picture = models.CharField(max_length=40, null=True)
