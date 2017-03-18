from django.conf.urls import url

from . import views


urlpatterns = [

    # Main website pages.
    url(r'^$', views.index, name='index'),
    url(r'^rules/$', views.rules, name='rules'),
    url(r'^info/$', views.info, name='info'),
    url(r'^about/$', views.about, name='about'),
    url(r'^archive/$', views.archive, name='archive'),
    url(r'^topics/$', views.topics, name='topics'),

    # Account actions
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),

    # Team editing
    url(r'^teams/$', views.display_teams, name='teams'),
    url(r'^teams/edit/(\d+)?$', views.edit_team, name='edit_team'),
    url(r'^teams/remove/(\d+)$', views.remove_team, name='remove_team'),

]
