from django.conf.urls import patterns, include, url
from django.contrib import admin
from users import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'partyup.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/register', views.register, name='register'),
    url(r'^users/login', views.login_view, name='login'),
    url(r'^event/create', views.create_event, name='create_event'),
)
