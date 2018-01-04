from django.conf.urls import url

from . import views


urlpatterns = [

    # Account actions
    url(r"^register/$", views.register, name="register"),

    # Team editing
    url(r"^teams/$", views.display_teams, name="teams"),
    url(r"^teams/edit/(\d+)?$", views.edit_team, name="edit_team"),
    url(r"^teams/remove/(\d+)$", views.remove_team, name="remove_team"),

]
