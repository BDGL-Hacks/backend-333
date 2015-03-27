from django.conf.urls import patterns, include, url
from django.contrib import admin
from users import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'partyup.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', views.register, name='register'),
)
