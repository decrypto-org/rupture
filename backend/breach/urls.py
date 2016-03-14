from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get_work/(?P<victim_id>\d+)$', views.get_work, name='get_work'),
    url(r'^get_work$', views.get_work, name='get_work'),
    url(r'^work_completed/(?P<victim_id>\d+)$', views.work_completed, name='work_completed'),
    url(r'^work_completed$', views.work_completed, name='work_completed')
]
