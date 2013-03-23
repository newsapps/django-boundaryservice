import json
from tastypie.serializers import Serializer
from django.template.loader import render_to_string
from django.core.serializers.json import DjangoJSONEncoder


class GeoSerializer(Serializer):
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
    
    def to_geojson(self, data, options=None):
        """
        Converts the bundle to a GeoJSON seralization.
        """
        # Hook the GeoJSON output to the object
        simple_obj = self.to_simple(data, options)
        shape_attr = self.sniff_shape_attr(data)
        simple_obj['geojson'] = getattr(data.obj, shape_attr).geojson
        # Get the properties serialized in GeoJSON style
        properties = dict(
            (k, v) for k, v in simple_obj.items()
                if k not in ['shape', 'simple_shape', 'geojson']
        )
        simple_obj['properties_json'] = json.dumps(
            properties,
            cls=DjangoJSONEncoder,
            sort_keys=True
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
