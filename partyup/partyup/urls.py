from django.conf.urls import patterns, include, url
from django.contrib import admin
from users.views import views, events, accounts, groups, messages

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^users/batch', accounts.user_batch),
    url(r'^users/login', accounts.login_view, name='login'),
    url(r'^users/picture/delete', accounts.user_picture_delete),
    url(r'^users/picture/upload', accounts.user_picture_upload),
    url(r'^users/register', accounts.register, name='register'),
    url(r'^users/search', accounts.user_search),

    url(r'^groups/create', groups.create_group, name='create_group'),
    url(r'^groups/get', groups.group_get),
    url(r'^groups/getid', groups.group_getid, name='group_getid'),
    url(r'^groups/messages/post', messages.messages_post, name='messages_post'),
    url(r'^groups/messages/get', messages.messages_get),
    url(r'^groups/picture/delete', groups.group_picture_delete),
    url(r'^groups/picture/upload', groups.group_picture_upload),

    url(r'^events/create', events.event_create, name='create_event'),
    url(r'^events/get', events.event_get),
    url(r'^events/picture/delete', events.event_picture_delete),
    url(r'^events/picture/upload', events.event_picture_upload),
    url(r'^events/search', events.event_search),
)
