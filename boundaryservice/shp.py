# -*- coding: utf-8 -*-
import os
import zipfile
import tempfile
import datetime
from osgeo import ogr, osr
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.contrib.gis.db.models.fields import GeometryField
from django.contrib.gis.gdal import check_err, OGRGeomType

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class ShpSerializer(object):
    """
    Mashes a queryset into a zip response.
    
    Modified from the ShpResponer in Dane Springmeyer's django-shapes.
    """
    def __init__(self, queryset, readme=None, geo_field=None, file_name='boundary-set',
        excludes=[]):
        self.queryset = queryset
        self.readme = readme
        self.geo_field = geo_field
        self.file_name = file_name
        self.excludes = excludes
    
    def __call__(self, *args, **kwargs):
        tmp = self.write_shapefile_to_tmp_file(self.queryset)
        return self.zip_response(tmp,self.file_name,self.readme)
    
    def get_metadata_attr(self):
        fields = []
        for obj in self.queryset:
            cand_list = [
                f for f in obj.metadata.keys()
            ]
            for cand in cand_list:
                if cand not in fields:
                    fields.append(cand)
        return fields
    
    def get_attributes(self):
        fields = self.queryset[0].__class__._meta.fields
        attr = [f for f in fields if not isinstance(f, GeometryField)
            and f.name not in self.excludes]
        return attr
    
    def get_geo_field(self):
        geo_field_by_name = [fld for fld 
            in self.queryset[0].__class__._meta.fields 
            if fld.name == self.geo_field
        ]
        if not geo_field_by_name:
            raise ValueError("Geodjango geometry field not found with the name '%s'" % (self.geo_field))
        else:
            geo_field = geo_field_by_name[0]
        return geo_field
    
    def write_shapefile_to_tmp_file(self,queryset):
        tmp = tempfile.NamedTemporaryFile(suffix='.shp', mode = 'w+b')
        # we must close the file for GDAL to be able to open and write to it
        tmp.close()
        args = tmp.name, queryset, self.get_geo_field()
        self.write_with_native_bindings(*args)
        return tmp.name
    
    def zip_response(self,shapefile_path,file_name,readme=None):
        buffer = StringIO()
        zip = zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED)
        files = ['shp','shx','prj','dbf']
        for item in files:
            filename = '%s.%s' % (shapefile_path.replace('.shp',''), item)
            zip.write(filename, arcname='%s.%s' % (file_name.replace('.shp',''), item))
        if readme:
            zip.writestr('README.txt',readme)
        zip.close()
        buffer.flush()
        zip_stream = buffer.getvalue()
        buffer.close()
        return zip_stream
    
    def create_field(self, layer, name):
        field_defn = ogr.FieldDefn(str(name)[:10], ogr.OFTString)
        field_defn.SetWidth(255)
        if layer.CreateField(field_defn) != 0:
            raise Exception('Faild to create field')
    
    def set_field(self, feat, name, value):
        try:
            string_value = str(value)
        except UnicodeEncodeError, E:
            string_value = ''
        feat.SetField(str(name)[:10], string_value)
    
    def write_with_native_bindings(self,tmp_name,queryset,geo_field):
        """ Write a shapefile out to a file from a geoqueryset.
        
        Written by Jared Kibele and Dane Springmeyer.
        
        In this case we use the python bindings available with a build
        of gdal when compiled with --with-python, instead of the ctypes-based 
        bindings that GeoDjango provides.
        
        """
        dr = ogr.GetDriverByName('ESRI Shapefile')
        ds = dr.CreateDataSource(tmp_name)
        if ds is None:
            raise Exception('Could not create file!')
        
        if hasattr(geo_field,'geom_type'):
            ogr_type = OGRGeomType(geo_field.geom_type).num
        else:
            ogr_type = OGRGeomType(geo_field._geom).num
        
        native_srs = osr.SpatialReference()
        if hasattr(geo_field,'srid'):
            native_srs.ImportFromEPSG(geo_field.srid)
        else:
            native_srs.ImportFromEPSG(geo_field._srid)
        
        layer = ds.CreateLayer('lyr', srs=native_srs, geom_type=ogr_type)
        
        # Get the standard shape attributes
        attributes = self.get_attributes()
        
        # Create columns for the standard shape attributes
        [self.create_field(layer, field.name) for field in attributes]
        
        # Create columnes for all the possible metadata attributes
        [self.create_field(layer, key) for key in self.get_metadata_attr()]
        
        feature_def = layer.GetLayerDefn()
        
        for item in queryset:
            feat = ogr.Feature( feature_def )
            
            for field in attributes:
                value = getattr(item, field.name)
                self.set_field(feat, field.name, value)
            
            for key, value in item.metadata.items():
                self.set_field(feat, key, value)
            
            geom = getattr(item, geo_field.name)
            if geom:
                ogr_geom = ogr.CreateGeometryFromWkt(geom.wkt)
                check_err(feat.SetGeometry(ogr_geom))
            else:
                pass
            
            check_err(layer.CreateFeature(feat))
        
        ds.Destroy()
