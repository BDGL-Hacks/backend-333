from django.conf.urls import patterns, url
from web import views

urlpatterns = patterns(
    '',
    url(r'groups/home/', views.groups_home),
    url(r'groups/ping/', views.groups_ping),
    url(r'groups/events/', views.groups_events),
    url(r'^$', views.homepage),
)
