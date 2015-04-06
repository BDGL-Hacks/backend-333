from django.conf.urls import patterns, include, url
from django.contrib import admin
from users.views import views, events

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/register', views.register, name='register'),
    url(r'^users/login', views.login_view, name='login'),
    url(r'^users/search', views.user_search),
    url(r'^events/search', events.event_search),
)
