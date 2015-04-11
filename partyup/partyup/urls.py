from django.conf.urls import patterns, include, url
from django.contrib import admin
from users.views import views, events, accounts

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/register', accounts.register, name='register'),
    url(r'^users/login', accounts.login_view, name='login'),
    url(r'^users/search', accounts.user_search),
    url(r'^groups/create', views.create_group, name='create_group'),
    url(r'^events/create', events.event_create, name='create_event'),
    url(r'^events/get', events.event_get),
    url(r'^events/search', events.event_search),
)
