from django.conf.urls import patterns, url
from users.views import events, accounts, groups, messages, invites

urlpatterns = patterns(
    '',
    url(r'^users/batch', accounts.user_batch),
    url(r'^users/login', accounts.login_view, name='login'),
    url(r'^users/picture/delete', accounts.user_picture_delete),
    url(r'^users/picture/upload', accounts.user_picture_upload),
    url(r'^users/register', accounts.register, name='register'),
    url(r'^users/search', accounts.user_search),

    url(r'^invites/respond', invites.respond_invite),

    url(r'^groups/addevent', groups.group_add_events),
    url(r'^groups/create', groups.group_create, name='create_group'),
    url(r'^groups/get/?$', groups.group_get),
    url(r'^groups/getid/?$', groups.group_getid, name='group_getid'),
    url(r'^groups/invite', invites.group_invite_view),
    url(r'^groups/currentevent', groups.group_change_currentevent),
    url(r'^groups/status', groups.group_update_status),
    url(r'^groups/ping/send', groups.group_ping_send),
    url(r'^groups/ping/respond', groups.group_ping_respond),
    url(r'^groups/messages/post', messages.messages_post, name='messages_post'),
    url(r'^groups/messages/get', messages.messages_get),
    url(r'^groups/picture/delete', groups.group_picture_delete),
    url(r'^groups/picture/upload', groups.group_picture_upload),

    url(r'^events/create', events.event_create, name='create_event'),
    url(r'^events/get/?$', events.event_get),
    url(r'^events/getattending/?$', events.event_getattending),
    url(r'^events/getid/?$', events.event_getid),
    url(r'^events/picture/delete', events.event_picture_delete),
    url(r'^events/picture/upload', events.event_picture_upload),
    url(r'^events/search', events.event_search),
    url(r'^events/invite', invites.event_invite_view),
)
