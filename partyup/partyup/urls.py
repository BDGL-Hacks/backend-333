from django.conf.urls import patterns, include, url
from django.contrib import admin
from users.views import views, events

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/register', views.register, name='register'),
    url(r'^users/login', views.login_view, name='login'),
    url(r'^users/search', views.user_search),
    url(r'^groups/create', views.create_group, name='create_group'),
    url(r'^events/create', views.create_event, name='create_event'),
    url(r'^events/search', events.event_search),
)
