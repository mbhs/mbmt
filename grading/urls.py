from django.conf.urls import url

from . import views


urlpatterns = [

    url(r"^$", views.index, name="index"),

    # Grading views
    url(r"^grade/students/$", views.StudentsView.as_view(), name="students"),
    url(r"^grade/teams/$", views.TeamsView.as_view(), name="teams"),
    url(r"^grade/(?P<grouping>\w+)/(?P<any_id>\d+)/(?P<round_id>\w+)/$", views.score, name="score"),
    url(r"^grade/statistics/$", views.statistics, name="statistics"),

    # Logistics
    url(r"^attendance/$", views.attendance, name="attendance"),
    url(r"^api/attendance/$", views.attendance_get, name="api_attendance"),

    url(r"^shirts/$", views.shirt_sizes, name="shirt_sizes"),
    url(r"^tags/students/$", views.student_name_tags, name="tags_students"),
    url(r"^tags/teachers/$", views.teacher_name_tags, name="tags_teachers"),
    url(r"^tags/chaperones/$", views.chaperone_name_tags, name="tags_chaperones"),

    # Scoring
    url(r"^scoreboard/students/$", views.student_scoreboard, name="scoreboard_students"),
    url(r"^scoreboard/teams/$", views.team_scoreboard, name="scoreboard_teams"),
    url(r"^live/(?P<round_id>\w+)/update/$", views.live_update, name="live_update"),
    url(r"^live/(?P<round_id>\w+)/$", views.live, name="live"),

    # Sponsor scores
    url(r"^scoreboard/sponsors/$", views.sponsor_scoreboard, name="scoreboard_sponsors"),

]
