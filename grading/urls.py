from django.conf.urls import url

from . import views


urlpatterns = [

    # Sponsor scores
    url(r'^teams/scores/$', views.sponsor_scoreboard, name='sponsor_scoreboard'),

    # Grading views
    url(r'^grade/students/$', views.view_students, name='student_view'),
    url(r'^grade/teams/$', views.view_teams, name="team_view"),
    url(r'^grade/teams/edit$', views.edit_teams, name="team_edit"),
    url(r'^grade/(?P<grouping>\w+)/(?P<id>\d+)/(?P<round>\w+)/$', views.score, name='score'),
    url(r'^grade/statistics/$', views.view_statistics, name="statistics"),

    # Logistics
    url(r'^shirts/$', views.shirts, name="shirts"),
    url(r'^attendance/$', views.attendance, name="attendance"),
    url(r'^tags/students/$', views.student_name_tags, name="student_name_tags"),
    url(r'^tags/teachers/$', views.teacher_name_tags, name="teacher_name_tags"),

    # Scoring
    url(r'^scoreboard/students/$', views.student_scoreboard, name="student_scoreboard"),
    url(r'^scoreboard/teams/$', views.team_scoreboard, name="team_scoreboard"),
    url(r'^live/(?P<round>\w+)/update/$', views.live_update, name='live_update'),
    url(r'^live/(?P<round>\w+)/$', views.live, name='live'),

]
