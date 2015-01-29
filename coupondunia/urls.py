from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import cricket.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'coupondunia.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', cricket.views.index, name='index'),
    url(r'^login$', cricket.views.login, name='login'),
    url(r'^logout$', cricket.views.logout, name='logout'),
    url(r'^register$', cricket.views.register, name='register'),
    url(r'^dashboard$', cricket.views.dashboard, name='manage'),
    url(r'^dashboard/addnewplayer$', cricket.views.addplayer, name='addplayer'),
    url(r'^dashboard/delete', cricket.views.delete, name='delete'),

    url(r'^player(?:/(?P<id>[0-9]+))?$', cricket.views.player, name='player'),
    url(r'^user(?:/(?P<id>[0-9]+))?$', cricket.views.user, name='user'),
    url(r'^team(?:/(?P<id>[0-9]+))?$', cricket.views.team, name='team'),

    url(r'^admin/', include(admin.site.urls)),

)
