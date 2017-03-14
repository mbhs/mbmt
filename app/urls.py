from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^rules/$', views.rules, name='rules'),
    url(r'^info/$', views.info, name='info'),
    url(r'^about/$', views.about, name='about'),
    url(r'^archive/$', views.archive, name='archive'),

    url(r'^grade/students$', views.grade_students, name='grade_students'),
    url(r'^grade/teams$', views.grade_teams, name="grade_teams"),
    url(r'^grade/(?P<grouping>\w+)/(?P<id>\d+)/(?P<round>\w+)$', views.score, name='score'),

    url(r'^attendance/$', views.attendance, name="attendance"),
    url(r'^scoreboard/$', views.scoreboard, name="scoreboard"),

    url(r'^topics/$', views.topics, name='topics'),
    url(r'^registration/$', views.registration, name='registration'),

    url(r'^teams/$', views.teams, name='teams'),
    url(r'^teams/edit/(\d+)?$', views.edit_team, name='edit_team'),
    url(r'^teams/remove/(\d+)$', views.remove_team, name='remove_team'),

    url(r'^accounts/register/$', views.register, name='register'),
    url(r'^accounts/login/$', views.login, name='login'),
    url(r'^accounts/logout/$', views.logout, name='logout'),

    url(r'^shirts/$', views.shirts, name="shirts"),
]
