import json
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from django.template.loader import render_to_string
from django.core.serializers.json import DjangoJSONEncoder


class BaseGeoSerializer(Serializer):
    """
    Adds some common geospatial outputs to the standard serializer.
    
    Supported formats:
        
        * JSON (Standard issue)
        * JSONP (Standard issue)
        * KML
        * GeoJSON
    
    """
    formats = [
        'json',
        'jsonp',
        'kml',
        'geojson',
    ]
    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
        'kml': 'application/vnd.google-earth.kml+xml',
        'geojson': 'application/geo+json',
    }
    
    def sniff_shape_attr(self, data):
        """
        Inspect the request and figure out which shape type
        the user would like us to return.
        """
        if data.request.GET.get('shape_type', '') == 'full':
            return 'shape'
        else:
            return 'simple_shape'


class BoundarySetGeoSerializer(BaseGeoSerializer):

    def to_geojson(self, data, options=None):
        """
        Converts the bundle to a GeoJSON seralization.
        """
        # Hook the GeoJSON output to the object
        simple_obj = self.to_simple(data, options)
        shape_attr = self.sniff_shape_attr(data)
        # Clean up the boundaries
        boundary_list = []
        for boundary in data.obj.boundaries.all():
            boundary.geojson = getattr(boundary, shape_attr).geojson
            boundary_list.append(boundary)
        # Render the result using a template and pass it out
        return render_to_string('object_list.geojson', {
            'boundary_set': simple_obj,
            'boundary_list': boundary_list,
        })
    
    def to_kml(self, data, options=None):
        """
        Converts the bundle to a KML serialization.
        """
        # Hook the KML output to the object
        simple_obj = self.to_simple(data, options)
        shape_attr = self.sniff_shape_attr(data)
        # Clean up the boundaries
        boundary_list = []
        for boundary in data.obj.boundaries.all():
            boundary.kml = getattr(boundary, shape_attr).kml
            boundary_list.append(boundary)
        # Render the result using a template and pass it out
        return render_to_string('object_list.kml', {
            'boundary_set': simple_obj,
            'boundary_list': boundary_list,
        })


class BoundaryGeoSerializer(BaseGeoSerializer):

    def to_geojson(self, data, options=None):
        """
        Converts the bundle to a GeoJSON seralization.
        """
        # Hook the GeoJSON output to the object
        simple_obj = self.to_simple(data, options)
        shape_attr = self.sniff_shape_attr(data)
        simple_obj['geojson'] = getattr(data.obj, shape_attr).geojson
        # Get the properties serialized in GeoJSON style
        simple_obj['properties'] = dict(
            (k, v) for k, v in simple_obj.items()
                if k not in ['shape', 'simple_shape', 'geojson']
        )
        # Render the result using a template and pass it out
        return render_to_string('object_detail.geojson', {
            'obj': simple_obj,
        })
    
    def to_kml(self, data, options=None):
        """
        Converts the bundle to a KML serialization.
        """
        # Hook the KML output to the object
        simple_obj = self.to_simple(data, options)
        shape_attr = self.sniff_shape_attr(data)
        simple_obj['kml'] = getattr(data.obj, shape_attr).kml
        # Render the result using a template and pass it out
        return render_to_string('object_detail.kml', {
            'obj': simple_obj,
        })
