from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login, name='login'),
    url(r'^rules/$', views.rules, name='rules'),
    url(r'^about/$', views.about, name='about'),
    url(r'^registration/$', views.registration, name='registration')
]
