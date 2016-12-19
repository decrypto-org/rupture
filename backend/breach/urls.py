from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get_work/(?P<victim_id>\d+)$', views.get_work, name='get_work'),
    url(r'^get_work$', views.get_work, name='get_work'),
    url(r'^work_completed/(?P<victim_id>\d+)$', views.work_completed, name='work_completed'),
    url(r'^work_completed$', views.work_completed, name='work_completed'),
    url(r'^target$', views.TargetView.as_view(), name='TargetView'),
    url(r'^victim$', views.VictimListView.as_view(), name='VictimListView'),
    url(r'^attack$', views.AttackView.as_view(), name='AttackView'),
    url(r'^victim/(?P<victim_id>\d+)/$', views.VictimDetailView.as_view(), name='VictimDetailView'),
    url(r'^victim/notstarted/$', views.DiscoveredVictimsView.as_view(), name='DiscoveredVictimsView')
]
