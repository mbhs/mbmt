from django.conf.urls import url

from . import views


urlpatterns = [

    url(r"^$", views.index, name="index"),

    # Registration
    url(r"^register/$", views.register, name="register"),
    url(r"^schools/$", views.schools, name="school"),
    url(r"^inactive/$", views.inactive, name="inactive"),

    # Team editing
    url(r"^teams/edit/(\d+)?$", views.edit_team, name="teams_edit"),
    url(r"^teams/remove/(\d+)$", views.remove_team, name="teams_remove"),

    url(r"^chaperones/edit/(d+)?$", views.edit_chaperone, name="chaperones_edit")

]
