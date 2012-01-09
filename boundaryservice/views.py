from django.contrib.gis.db import models
from django.http import Http404

from boundaryservice.base_views import (ModelListView, ModelDetailView,
                                        ModelGeoListView, ModelGeoDetailView)
from boundaryservice.models import BoundarySet, Boundary

class BoundarySetListView(ModelListView):
    """ e.g. /boundary-set/ """

    filterable_fields = ['name', 'domain', 'hierarchy']

    model = BoundarySet

class BoundarySetDetailView(ModelDetailView):
    """ e.g. /boundary-set/federal-electoral-districts/ """

    model = BoundarySet

    def get_object(self, request, qs, slug):
        try:
            return qs.get(slug=slug)
        except BoundarySet.DoesNotExist:
            raise Http404

class BoundaryListView(ModelGeoListView):
    """ e.g. /boundary/federal-electoral-districts/
    or /boundary/federal-electoral-districts/centroid """

    filterable_fields = ['external_id', 'name']
    allowed_geo_fields = ('shape', 'simple_shape', 'centroid')
    default_geo_filter_field = 'shape'
    model = Boundary

    def filter(self, request, qs):
        qs = super(BoundaryListView, self).filter(request, qs)

        if 'intersects' in request.GET:
            (set_slug, slug) = request.GET['intersects'].split('/')
            try:
                shape = Boundary.objects.filter(slug=slug, set=set_slug).values_list('shape', flat=True)[0]
            except IndexError:
                raise Http404
            qs = qs.filter(models.Q(shape__covers=shape) | models.Q(shape__overlaps=shape))

        if 'touches' in request.GET:
            (set_slug, slug) = request.GET['touches'].split('/')
            try:
                shape = Boundary.objects.filter(slug=slug, set=set_slug).values_list('shape', flat=True)[0]
            except IndexError:
                raise Http404
            qs = qs.filter(shape__touches=shape)

        if 'sets' in request.GET:
            set_slugs = request.GET['sets'].split(',')
            qs = qs.filter(set__in=set_slugs)

        return qs

    def get_qs(self, request, set_slug=None):
        qs = super(BoundaryListView, self).get_qs(request)
        if set_slug:
            return qs.filter(set=set_slug)
        return qs

class BoundaryObjectGetterMixin(object):

    model = Boundary

    def get_object(self, request, qs, set_slug, slug):
        try:
            return qs.get(slug=slug, set=set_slug)
        except Boundary.DoesNotExist:
            raise Http404

class BoundaryDetailView(ModelDetailView, BoundaryObjectGetterMixin):
    """ e.g. /boundary/federal-electoral-districts/outremont/ """

    def __init__(self):
        super(BoundaryDetailView, self).__init__()
        self.base_qs = self.base_qs.defer('shape', 'simple_shape', 'centroid')

class BoundaryGeoDetailView(ModelGeoDetailView, BoundaryObjectGetterMixin):
    """ e.g /boundary/federal-electoral-districts/outremont/shape """

    allowed_geo_fields = ('shape', 'simple_shape', 'centroid')





