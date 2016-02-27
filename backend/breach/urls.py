from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get_work$', views.get_work, name='get_work'),
    url(r'^work_completed$', views.work_completed, name='work_completed')
]
