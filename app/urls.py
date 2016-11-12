from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^rules/$', views.rules, name='rules'),
    url(r'^about/$', views.about, name='about'),

    url(r'^grade/all$', views.grade, name='grade'),
    url(r'^grade/score/(?P<type>.+)/(?P<id>\d+)$', views.score, name='score'),

    url(r'^topics/$', views.topics, name='topics'),
    url(r'^registration/$', views.registration, name='registration'),

    url(r'^teams/$', views.teams, name='teams'),
    url(r'^teams/add/$', views.add_team, name='add_team'),

    url(r'^accounts/register/$', views.register, name='register'),
    url(r'^accounts/login/$', views.login, name='login'),
    url(r'^accounts/logout/$', views.logout, name='logout')
]
