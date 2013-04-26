import json
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from boundaryservice.shp import ShpSerializer
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
        'shp',
    ]
    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
        'kml': 'application/vnd.google-earth.kml+xml',
        'geojson': 'application/geo+json',
        'shp': 'application/zip',
    }
    
    def get_shape_attr(self, shape_type):
        """
        Which shape attribute the user would like us to return.
        """
        if shape_type == 'full':
            return 'shape'
        else:
            return 'simple_shape'


class BoundarySetGeoSerializer(BaseGeoSerializer):
    """
    Applies the geospatial serializer to the BoundarySet model.
    """
    def to_shp(self, data, options=None):
        """
        Converts the bundle to a SHP serialization.
        """
        simple_obj = self.to_simple(data, options)
        if isinstance(data, dict):
            # List data
            shape_attr = self.get_shape_attr(data['shape_type'])
            boundary_list = []
            for bset in data['objects']:
                for boundary in bset.obj.boundaries.all():
                    boundary_list.append(boundary)
            return ShpSerializer(
                queryset=boundary_list,
                geo_field=shape_attr,
                excludes=['id', 'singular', 'kind_first', 'metadata'],
            )()
        elif isinstance(data, Bundle):
            # Detail data
            shape_attr = self.get_shape_attr(data.shape_type)
            boundary_list = []
            for boundary in data.obj.boundaries.all():
                boundary_list.append(boundary)
            return ShpSerializer(
                queryset=boundary_list,
                geo_field=shape_attr,
                readme=simple_obj['notes'],
                file_name=boundary_list[0].kind.lower(),
                excludes=['id', 'singular', 'kind_first', 'metadata'],
            )()
    
    def to_geojson(self, data, options=None):
        """
        Converts the bundle to a GeoJSON seralization.
        """
        # Hook the GeoJSON output to the object
        simple_obj = self.to_simple(data, options)
        if isinstance(data, dict):
            # List data
            shape_attr = self.get_shape_attr(data['shape_type'])
            boundary_list = []
            for bset in data['objects']:
                simple_bset = self.to_simple(bset, options)
                for boundary in bset.obj.boundaries.all():
                    boundary.geojson = getattr(boundary, shape_attr).geojson
                    boundary.set_uri = simple_bset['resource_uri']
                    api_name = "".join(boundary.set_uri.split("/")[:2])
                    boundary.resource_uri = "/%s/boundary/%s/" % (api_name, boundary.slug)
                    boundary_list.append(boundary)
            geojson = json.loads(render_to_string('object_list.geojson', {
                'boundary_list': boundary_list,
            }))
            response_dict = dict(meta=simple_obj['meta'], geojson=geojson)
            return json.dumps(
                response_dict,
                cls=DjangoJSONEncoder,
                sort_keys=False,
                ensure_ascii=False
            )
        elif isinstance(data, Bundle):
            shape_attr = self.get_shape_attr(data.shape_type)
            # Clean up the boundaries
            boundary_list = []
            for boundary in data.obj.boundaries.all():
                boundary.geojson = getattr(boundary, shape_attr).geojson
                boundary.set_uri = simple_obj['resource_uri']
                api_name = "".join(boundary.set_uri.split("/")[:2])
                boundary.resource_uri = "/%s/boundary/%s/" % (api_name, boundary.slug)
                boundary_list.append(boundary)
            # Render the result using a template and pass it out
            return render_to_string('object_list.geojson', {
                'boundary_list': boundary_list,
            })
    
    def to_kml(self, data, options=None):
        """
        Converts the bundle to a KML serialization.
        """
        # Hook the GeoJSON output to the object
        simple_obj = self.to_simple(data, options)
        if isinstance(data, dict):
            # List data
            shape_attr = self.get_shape_attr(data['shape_type'])
            boundary_list = []
            for bset in data['objects']:
                simple_bset = self.to_simple(bset, options)
                for boundary in bset.obj.boundaries.all():
                    boundary.kml = getattr(boundary, shape_attr).kml
                    boundary.set_uri = simple_bset['resource_uri']
                    api_name = "".join(boundary.set_uri.split("/")[:2])
                    boundary.resource_uri = "/%s/boundary/%s/" % (api_name, boundary.slug)
                    boundary_list.append(boundary)
            return render_to_string('object_list.kml', {
                'boundary_list': boundary_list,
            })
        elif isinstance(data, Bundle):
            shape_attr = self.get_shape_attr(data.shape_type)
            # Clean up the boundaries
            boundary_list = []
            for boundary in data.obj.boundaries.all():
                boundary.kml = getattr(boundary, shape_attr).kml
                boundary.set_uri = simple_obj['resource_uri']
                api_name = "".join(boundary.set_uri.split("/")[:2])
                boundary.resource_uri = "/%s/boundary/%s/" % (api_name, boundary.slug)
                boundary_list.append(boundary)
            # Render the result using a template and pass it out
            return render_to_string('object_list.kml', {
                'boundary_list': boundary_list,
            })


class BoundaryGeoSerializer(BaseGeoSerializer):
    """
    Applies the geospatial serializer to the Boundary model.
    """
    def to_shp(self, data, options=None):
        """
        Converts the bundle to a SHP serialization.
        """
        # Hook the KML output to the object
        simple_obj = self.to_simple(data, options)
        # Figure out if it's list data or detail data
        if isinstance(data, dict):
            # List data
            shape_attr = self.get_shape_attr(data['shape_type'])
            boundary_list = []
            for bundle in data['objects']:
                boundary_list.append(bundle.obj)
            return ShpSerializer(
                queryset=boundary_list,
                geo_field=shape_attr,
                excludes=['id', 'singular', 'kind_first', 'metadata'],
            )()
        
        elif isinstance(data, Bundle):
            # Detail data
            shape_attr = self.get_shape_attr(data.shape_type)
            simple_obj['kml'] = getattr(data.obj, shape_attr).kml
            return ShpSerializer(
                queryset=[data.obj],
                geo_field=shape_attr,
                file_name=data.obj.kind.lower(),
                excludes=['id', 'singular', 'kind_first', 'metadata'],
            )()

    def to_geojson(self, data, options=None):
        """
        Converts the bundle to a GeoJSON seralization.
        """
        simple_obj = self.to_simple(data, options)
        # Figure out if it's list data or detail data
        if isinstance(data, dict):
            # List data
            shape_attr = self.get_shape_attr(data['shape_type'])
            boundary_list = []
            for bundle in data['objects']:
                simple_boundary = self.to_simple(bundle, options)
                simple_boundary['geojson'] = getattr(bundle.obj, shape_attr).geojson
                simple_boundary['set_uri'] = simple_boundary['set']
                boundary_list.append(simple_boundary)
            geojson = json.loads(render_to_string('object_list.geojson', {
                'boundary_list': boundary_list,
            }))
            response_dict = dict(meta=simple_obj['meta'], geojson=geojson)
            return json.dumps(
                response_dict,
                cls=DjangoJSONEncoder,
                sort_keys=False,
                ensure_ascii=False
            )
            
        elif isinstance(data, Bundle):
            # Detail data
            shape_attr = self.get_shape_attr(data.shape_type)
            simple_obj['geojson'] = getattr(data.obj, shape_attr).geojson
            simple_obj['set_uri'] = simple_obj['set']
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
        # Figure out if it's list data or detail data
        if isinstance(data, dict):
            # List data
            shape_attr = self.get_shape_attr(data['shape_type'])
            boundary_list = []
            for bundle in data['objects']:
                simple_boundary = self.to_simple(bundle, options)
                simple_boundary['kml'] = getattr(bundle.obj, shape_attr).kml
                simple_boundary['set_uri'] = simple_boundary['set']
                boundary_list.append(simple_boundary)
            return render_to_string('object_list.kml', {
                'boundary_list': boundary_list,
            })
        
        elif isinstance(data, Bundle):
            # Detail data
            shape_attr = self.get_shape_attr(data.shape_type)
            simple_obj['kml'] = getattr(data.obj, shape_attr).kml
            simple_obj['set_uri'] = simple_obj['set']
            # Render the result using a template and pass it out
            return render_to_string('object_detail.kml', {
                'obj': simple_obj,
            })
