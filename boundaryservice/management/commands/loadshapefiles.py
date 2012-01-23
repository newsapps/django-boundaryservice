#coding: utf8

import logging
log = logging.getLogger(__name__)
from optparse import make_option
import os, os.path
import sys

from zipfile import ZipFile
from tempfile import mkdtemp

from django.conf import settings
from django.contrib.gis.gdal import CoordTransform, DataSource, OGRGeometry, OGRGeomType
from django.core.management.base import BaseCommand
from django.db import connections, DEFAULT_DB_ALIAS, transaction
from django.template.defaultfilters import slugify

import boundaryservice
from boundaryservice.models import BoundarySet, Boundary, app_settings

GEOMETRY_COLUMN = 'shape'

class Command(BaseCommand):
    help = 'Import boundaries described by shapefiles.'
    option_list = BaseCommand.option_list + (
        make_option('-r', '--reload', action='store_true', dest='reload',
            help='Reload BoundarySets that have already been imported.'),
        make_option('-d', '--data-dir', action='store', dest='data_dir', 
            default=app_settings.SHAPEFILES_DIR,
            help='Load shapefiles from this directory'),
        make_option('-e', '--except', action='store', dest='except',
            default=False, help='Don\'t load these kinds of Areas, comma-delimited.'),
        make_option('-o', '--only', action='store', dest='only',
            default=False, help='Only load these kinds of Areas, comma-delimited.'),
        make_option('-u', '--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Specify a database to load shape data into.'),
    )

    def get_version(self):
        return '0.1'

    def handle(self, *args, **options):
        # Load configuration
        boundaryservice.autodiscover(options['data_dir'])

        all_sources = boundaryservice.registry

        if options['only']:
            only = options['only'].split(',')
            # TODO: stripping whitespace here because optparse doesn't handle it correctly
            sources = [s for s in all_sources if s.replace(' ', '') in only]
        elif options['except']:
            exceptions = options['except'].upper().split(',')
            # See above
            sources = [s for s in all_sources if s.replace(' ', '') not in exceptions]
        else:
            sources = [s for s in all_sources]
        
        for kind, config in all_sources.items():
            if kind not in sources:
                log.debug('Skipping %s.' % kind)
                continue

            if (not options['reload']) and BoundarySet.objects.filter(name=kind).exists():
                log.info('Already loaded %s, skipping.' % kind)
                continue

            self.load_set(kind, config, options)

    @transaction.commit_on_success
    def load_set(self, kind, config, options):
        log.info('Processing %s.' % kind)

        BoundarySet.objects.filter(name=kind).delete()

        path = config['file']
        datasources = create_datasources(path)

        layer = datasources[0][0]

        # Add some default values
        if 'singular' not in config and kind.endswith('s'):
            config['singular'] = kind[:-1]
        if 'id_func' not in config:
            config['id_func'] = lambda f: ''
        if 'slug_func' not in config:
            config['slug_func'] = config['name_func']

        # Create BoundarySet
        set = BoundarySet.objects.create(
            name=kind,
            singular=config['singular'],
            authority=config.get('authority', ''),
            domain=config.get('domain', ''),
            last_updated=config.get('last_updated'),
            source_url=config.get('source_url', ''),
            notes=config.get('notes', ''),
            licence_url=config.get('licence_url', ''),
        )

        for datasource in datasources:
            log.info("Loading %s from %s" % (kind, datasource.name))
            # Assume only a single-layer in shapefile
            if datasource.layer_count > 1:
                log.warn('%s shapefile [%s] has multiple layers, using first.' % (datasource.name, kind))
            layer = datasource[0]
            self.add_boundaries_for_layer(config, layer, set, options['database'])

        log.info('%s count: %i' % (kind, Boundary.objects.filter(set=set).count()))

    def polygon_to_multipolygon(self, geom):
        """
        Convert polygons to multipolygons so all features are homogenous in the database.
        """
        if geom.__class__.__name__ == 'Polygon':
            g = OGRGeometry(OGRGeomType('MultiPolygon'))
            g.add(geom)
            return g
        elif geom.__class__.__name__ == 'MultiPolygon':
            return geom
        else:
            raise ValueError('Geom is neither Polygon nor MultiPolygon.')

    def add_boundaries_for_layer(self, config, layer, set, database):
        # Get spatial reference system for the postgis geometry field
        geometry_field = Boundary._meta.get_field_by_name(GEOMETRY_COLUMN)[0]
        SpatialRefSys = connections[database].ops.spatial_ref_sys()
        db_srs = SpatialRefSys.objects.using(database).get(srid=geometry_field.srid).srs

        if 'srid' in config and config['srid']:
            layer_srs = SpatialRefSys.objects.get(srid=config['srid']).srs
        else:
            layer_srs = layer.srs

        # Create a convertor to turn the source data into
        transformer = CoordTransform(layer_srs, db_srs)

        for feature in layer:
            # Transform the geometry to the correct SRS
            geometry = self.polygon_to_multipolygon(feature.geom)
            geometry.transform(transformer)

            # Create simplified geometry field by collapsing points within 1/1000th of a degree.
            # Since Chicago is at approx. 42 degrees latitude this works out to an margin of 
            # roughly 80 meters latitude and 112 meters longitude.
            # Preserve topology prevents a shape from ever crossing over itself.
            simple_geometry = geometry.geos.simplify(app_settings.SIMPLE_SHAPE_TOLERANCE, preserve_topology=True)
            
            # Conversion may force multipolygons back to being polygons
            simple_geometry = self.polygon_to_multipolygon(simple_geometry.ogr)

            feature = UnicodeFeature(feature, encoding=config.get('encoding', 'ascii'))

            # Extract metadata into a dictionary
            metadata = dict(
                ( (field, feature.get(field)) for field in layer.fields )
            )

            external_id = str(config['id_func'](feature))
            feature_name = config['name_func'](feature)
            feature_slug = slugify(config['slug_func'](feature).replace(u'—', '-'))

            Boundary.objects.create(
                set=set,
                set_name=set.singular,
                external_id=external_id,
                name=feature_name,
                slug=feature_slug,
                metadata=metadata,
                shape=geometry.wkt,
                simple_shape=simple_geometry.wkt,
                centroid=geometry.geos.centroid)
        
def create_datasources(path):
    if path.endswith('.zip'):
        path = temp_shapefile_from_zip(path)

    if path.endswith('.shp'):
        return [DataSource(path)]
    
    # assume it's a directory...
    sources = []
    for fn in os.listdir(path):
        fn = os.path.join(path,fn)
        if fn.endswith('.zip'):
            fn = temp_shapefile_from_zip(fn)
        if fn.endswith('.shp'):
            sources.append(DataSource(fn))
    return sources

class UnicodeFeature(object):

    def __init__(self, feature, encoding='ascii'):
        self.feature = feature
        self.encoding = encoding

    def get(self, field):
        val = self.feature.get(field)
        if isinstance(val, str):
            return val.decode(self.encoding)
        return val
    
def temp_shapefile_from_zip(zip_path):
    """Given a path to a ZIP file, unpack it into a temp dir and return the path
       to the shapefile that was in there.  Doesn't clean up after itself unless 
       there was an error.

       If you want to cleanup later, you can derive the temp dir from this path.
    """
    zf = ZipFile(zip_path)
    tempdir = mkdtemp()
    shape_path = None
    # Copy the zipped files to a temporary directory, preserving names.
    for name in zf.namelist():
        data = zf.read(name)
        outfile = os.path.join(tempdir, name)
        if name.endswith('.shp'):
            shape_path = outfile
        f = open(outfile, 'w')
        f.write(data)
        f.close()

    if shape_path is None:
        log.warn("No shapefile, cleaning up")
        # Clean up after ourselves.
        for file in os.listdir(tempdir):
            os.unlink(os.path.join(tempdir, file))
        os.rmdir(tempdir)
        raise ValueError("No shapefile found in zip")
    
    return shape_path
