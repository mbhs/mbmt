from django.conf.urls import url

from . import views


urlpatterns = [

    url(r"^$", views.index, name="index"),

    # Registration
    url(r"^register/$", views.register, name="register"),
    url(r"^schools/$", views.schools, name="school"),
    url(r"^inactive/$", views.inactive, name="inactive"),

    # Team editing
    url(r"^teams/edit/(\d+)?$", views.team_edit, name="team_edit"),
    url(r"^teams/remove/(\d+)$", views.team_remove, name="team_remove"),

    url(r"^chaperones/edit/(\d+)?", views.chaperone_edit, name="chaperone_edit"),
    url(r"^chaperones/remove/(\d+)?", views.chaperone_remove, name="chaperone_remove")

]
