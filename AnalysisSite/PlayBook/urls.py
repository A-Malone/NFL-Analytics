from django.conf.urls import patterns, url
from PlayBook import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<game_id>\w+)/$', views.viewGame, name='viewGame'),
    url(r'^(?P<game_id>\w+)/json/$', views.get_play, name='getPlay'),
)