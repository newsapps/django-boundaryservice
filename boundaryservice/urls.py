from django.conf.urls.defaults import patterns, include, url

from boundaryservice.views import *

urlpatterns = patterns('',
    url(r'^boundary-set/$', BoundarySetListView.as_view(), name='boundaryservice_set_list'),
    url(r'^boundary-set/(?P<slug>[\w_-]+)/$', BoundarySetDetailView.as_view(), name='boundaryservice_set_detail'),
    url(r'^boundary/$', BoundaryListView.as_view(), name='boundaryservice_boundary_list'),
    url(r'^boundary/(?P<geo_field>shape|simple_shape|centroid)$', BoundaryListView.as_view()),
    url(r'^boundary/(?P<set_slug>[\w_-]+)/$', BoundaryListView.as_view(), name='boundaryservice_boundary_list'),
    url(r'^boundary/(?P<set_slug>[\w_-]+)/(?P<geo_field>shape|simple_shape|centroid)$', BoundaryListView.as_view()),
    url(r'^boundary/(?P<set_slug>[\w_-]+)/(?P<slug>[\w_-]+)/$', BoundaryDetailView.as_view(), name='boundaryservice_boundary_detail'),
    url(r'^boundary/(?P<set_slug>[\w_-]+)/(?P<slug>[\w_-]+)/(?P<geo_field>shape|simple_shape|centroid)$', BoundaryGeoDetailView.as_view()),
)
