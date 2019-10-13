from django.conf.urls import include, url
from tastypie.api import Api

from boundaryservice.resources import BoundarySetResource, BoundaryResource
from boundaryservice.views import external_id_redirects

v1_api = Api(api_name='1.0')
v1_api.register(BoundarySetResource())
v1_api.register(BoundaryResource())

urlpatterns = [
    url(r'^(?P<api_name>1.0)/(?P<resource_name>boundary-set)/(?P<slug>[\w\d_.-]+)/(?P<external_id>[\w\d_.-]+)$', external_id_redirects),
    url(r'', include(v1_api.urls)),
]
