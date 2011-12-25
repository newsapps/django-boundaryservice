""" A mini API framework.
"""

import re

from django.contrib.gis.measure import D
from django.http import HttpResponse, Http404
from django.template.defaultfilters import escapejs
from django.utils import simplejson as json
from django.views.generic import View

from tastypie.paginator import Paginator

from boundaryservice import kml

class RawJSONResponse(object):
    """APIView subclasses can return these if they have
    already-serialized JSON to return"""
    def __init__(self, content):
        self.content = content

class APIView(View):
    """Base view class that serializes subclass responses to JSON.

    Subclasses should define get/post/etc. methods."""

    allow_jsonp = True
    content_type = 'application/json; charset=utf-8'

    def dispatch(self, request, *args, **kwargs):
        result = super(APIView, self).dispatch(request, *args, **kwargs)
        if isinstance(result, HttpResponse):
            return result
        resp = HttpResponse(content_type=self.content_type)
        callback = ''
        if self.allow_jsonp and 'callback' in request.GET:
            callback = re.sub(r'[^a-zA-Z0-9_]', '', request.GET['callback'])
            resp.write(callback + '(')
        if isinstance(result, RawJSONResponse):
            resp.write(result.content)
        else:
            json.dump(result, resp, indent=4)
        if callback:
            resp.write(');')
        return resp

class ModelListView(APIView):
    """Base API class for a list of resources.

    Subclasses should set the 'model' attribute to the appropriate model class.
    Set the filterable_fields attribute to a list of field names users should
    be able to filter on.

    Compatible model classes should define a static method called get_dicts that,
    given a list of objects, returns a list of dicts suitable for serialization.
    By default, those will be model objects, but the model can also define a static
    method called 'prepare_queryset_for_get_dicts' that accepts a queryset and returns
    a sliceable iterable of objects that will later be passed to get_dicts."""

    filter_types = ['exact', 'iexact', 'contains', 'icontains',
                    'startswith', 'istartswith', 'endswith', 'iendswith', 'isnull']

    def get_qs(self, request):
        return self.model.objects.all()

    def filter(self, request, qs):
        for (f, val) in request.GET.items():
            if '__' in f:
                (filter_field, filter_type) = f.split('__')
            else:
                (filter_field, filter_type) = (f, 'exact')
            if filter_field in getattr(self, 'filterable_fields', []) and filter_type in self.filter_types:
                if val in ['true', 'True']:
                    val = True
                elif val in ['false', 'False']:
                    val = False
                qs = qs.filter(**{filter_field + '__' + filter_type: val})
        return qs

    def get(self, request, **kwargs):
        qs = self.get_qs(request, **kwargs)
        qs = self.filter(request, qs)
        if hasattr(self.model, 'prepare_queryset_for_get_dicts'):
            qs = self.model.prepare_queryset_for_get_dicts(qs)
        paginator = Paginator(request.GET, qs, resource_uri=request.path)
        result = paginator.page()
        result['objects'] = self.model.get_dicts(result['objects'])
        return result

class ModelGeoListView(ModelListView):
    """Adds geospatial support to ModelListView.

    Subclasses must set the 'allowed_geo_fields' attribute to a list
    of geospatial field names which we're allowed to provide.

    'name_field' should be the name of the field on objects that
     contains a name value

    To enable a couple of default geospatial filters, the
    default_geo_filter_field attribute should be set to the name
    of the geometry field to filter on.

    To access a geospatial field, the field name must be provided
    by the URLconf in the 'geo_field' keyword argument."""

    name_field = 'name'
    default_geo_filter_field = None

    def filter(self, request, qs):
        qs = super(ModelGeoListView, self).filter(request, qs)

        if self.default_geo_filter_field:
            if 'contains' in request.GET:
                lat, lon = re.sub(r'[^\d.,-]', '', request.GET['contains']).split(',')
                wkt_pt = 'POINT(%s %s)' % (lon, lat)
                qs = qs.filter(**{self.default_geo_filter_field + "__contains" : wkt_pt})

            if 'near' in request.GET:
                lat, lon, range = request.GET['near'].split(',')
                wkt_pt = 'POINT(%s %s)' % (float(lon), float(lat))
                numeral = re.match('([0-9]+)', range).group(1)
                unit = range[len(numeral):]
                numeral = int(numeral)
                kwargs = {unit: numeral}
                qs = qs.filter(**{self.default_geo_filter_field + "__distance_lte" :(wkt_pt, D(**kwargs))})

        return qs

    def get(self, request, **kwargs):
        if 'geo_field' not in kwargs:
            # If it's not a geo request, let ModelListView handle it.
            return super(ModelGeoListView, self).get(request, **kwargs)

        field = kwargs.pop('geo_field')
        if field not in self.allowed_geo_fields:
            raise Http404
        qs = self.get_qs(request, **kwargs)
        qs = self.filter(request, qs)

        format = request.GET.get('format', 'json')

        if format == 'json':
            strings = [u'{ "objects" : [ ']
            strings.append(','.join( (u'{"name": "%s","%s":%s}' % (escapejs(x[1]),field,x[0].geojson)
                        for x in qs.values_list(field, self.name_field) )))
            strings.append(u']}')
            return RawJSONResponse(u''.join(strings))
        elif format == 'wkt':
            return HttpResponse("\n".join((geom.wkt for geom in qs.values_list(field, flat=True))), mimetype="text/plain")
        elif format == 'kml':
            placemarks = [kml.generate_placemark(x[1], x[0]) for x in qs.values_list(field, self.name_field)]
            return HttpResponse(kml.generate_kml_document(placemarks), mimetype="application/vnd.google-earth.kml+xml")
        else:
            raise NotImplementedError

class ModelDetailView(APIView):
    """Return the API representation of a single object.

    Subclasses must set the 'model' attribute to the appropriate model class.
    Subclasses must define a 'get_object' method to return a single model
      object. Its argument will be the request, a QuerySet of objects from
      which to select, and any keyword arguments provided by the URLconf.

    Compatible model classes must define an as_dict instance method which
    returns a serializable dict of the object's data."""

    def __init__(self):
        super(ModelDetailView, self).__init__()
        self.base_qs = self.model.objects.all()

    def get(self, request, **kwargs):
        return self.get_object(request, self.base_qs, **kwargs).as_dict()

class ModelGeoDetailView(ModelDetailView):
    """Adds geospatial support to ModelDetailView

    Subclasses must set the 'allowed_geo_fields' attribute to a list
    of geospatial field names which we're allowed to provide.

    To access a geospatial field, the field name must be provided
    by the URLconf in the 'geo_field' keyword argument."""

    name_field = 'name'

    def get(self, request, **kwargs):
        if 'geo_field' not in kwargs:
            # If it's not a geo request, let ModelDetailView handle it.
            return super(ModelGeoDetailView, self).get(request, **kwargs)

        field = kwargs.pop('geo_field')
        if field not in self.allowed_geo_fields:
            raise Http404

        obj = self.get_object(request, self.base_qs.only(field, self.name_field), **kwargs)

        geom = getattr(obj, field)
        name = getattr(obj, self.name_field)
        format = request.GET.get('format', 'json')
        if format == 'json':
            return RawJSONResponse(geom.geojson)
        elif format == 'wkt':
            return HttpResponse(geom.wkt, mimetype="text/plain")
        elif format == 'kml':
            return HttpResponse(
                kml.generate_kml_document([kml.generate_placemark(name, geom)]),
                mimetype="application/vnd.google-earth.kml+xml")
        else:
            raise NotImplementedError