from django.conf.urls.defaults import patterns, include 
from tastypie.api import Api

from boundaryservice.resources import BoundarySetResource, BoundaryResource

v1_api = Api(api_name='1.0')
v1_api.register(BoundarySetResource())
v1_api.register(BoundaryResource())

urlpatterns = patterns('',
    (r'', include(v1_api.urls)),
)
