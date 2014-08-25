from django.conf.urls import patterns, url
from portfolio import views

urlpatterns = patterns('',
    # /portfolio/
    url(r'^$', views.index, name='index'),
    # /portfolio/1/
    url(r'^(?P<txn_id>\d+)/$', views.detail, name='detail'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^home/$', views.home, name='home'),
    url(r'^history/$', views.history, name='history'),
    url(r'^gains/$', views.gains, name='gains'),
    url(r'^portfolio/$', views.portfolio, name='portfolio'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
)
