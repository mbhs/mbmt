from django.conf.urls import url

from . import views


urlpatterns = [

    # Grading views
    url(r'^grade/students/$', views.view_students, name='grade_students'),
    url(r'^grade/teams/$', views.view_teams, name="grade_teams"),
    url(r'^grade/(?P<grouping>\w+)/(?P<id>\d+)/(?P<round>\w+)/$', views.score, name='score'),

    # Logistics
    url(r'^shirts/$', views.shirts, name="shirts"),
    url(r'^attendance/$', views.attendance, name="attendance"),
    url(r'^tags/student/$', views.student_name_tags, name="student_name_tags"),
    url(r'^tags/teacher/$', views.teacher_name_tags, name="teacher_name_tags"),

    # Scoring
    url(r'^scoreboard/$', views.scoreboard, name="scoreboard"),
    url(r'^live/(?P<round>\w+)/', views.live, name='live'),

]
