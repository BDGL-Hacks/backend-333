from django.conf.urls import patterns, include, url
from django.contrib import admin
from web import views

urlpatterns = patterns(
    '',
    url(r'groups/home/', views.groups_home),
    url(r'groups/ping/', views.groups_ping),
    url(r'groups/events/', views.groups_events),
    url(r'^$', views.homepage),
)
