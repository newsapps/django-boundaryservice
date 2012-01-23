from django.conf.urls.defaults import patterns, include, url

from boundaryservice.views import *

urlpatterns = patterns('',
    url(r'^boundary-sets/$', BoundarySetListView.as_view(), name='boundaryservice_set_list'),
    url(r'^boundary-sets/(?P<slug>[\w_-]+)/$', BoundarySetDetailView.as_view(), name='boundaryservice_set_detail'),
    url(r'^boundaries/$', BoundaryListView.as_view(), name='boundaryservice_boundary_list'),
    url(r'^boundaries/(?P<geo_field>shape|simple_shape|centroid)$', BoundaryListView.as_view(),
        name='boundaryservice_boundary_list'),
    url(r'^boundaries/(?P<set_slug>[\w_-]+)/$', BoundaryListView.as_view(), name='boundaryservice_boundary_list'),
    url(r'^boundaries/(?P<set_slug>[\w_-]+)/(?P<geo_field>shape|simple_shape|centroid)$', BoundaryListView.as_view(),
        name='boundaryservice_boundary_list'),
    url(r'^boundaries/(?P<set_slug>[\w_-]+)/(?P<slug>[\w_-]+)/$', BoundaryDetailView.as_view(),
        name='boundaryservice_boundary_detail'),
    url(r'^boundaries/(?P<set_slug>[\w_-]+)/(?P<slug>[\w_-]+)/(?P<geo_field>shape|simple_shape|centroid)$',
        BoundaryGeoDetailView.as_view(), name='boundaryservice_boundary_detail'),
)
