import re

from django.contrib.gis.db import models
from django.core import urlresolvers
from django.template.defaultfilters import slugify

from appconf import AppConf
from jsonfield import JSONField

class MyAppConf(AppConf):
    MAX_GEO_LIST_RESULTS = 350 # In a /boundary/shape query, if more than this
                        # number of resources are matched, throw an error
    SHAPEFILES_DIR = './data/shapefiles'
    SIMPLE_SHAPE_TOLERANCE = 0.0002

app_settings = MyAppConf()

class BoundarySet(models.Model):
    """
    A set of related boundaries, such as all Wards or Neighborhoods.
    """
    slug = models.SlugField(max_length=200, primary_key=True, editable=False)

    name = models.CharField(max_length=100, unique=True,
        help_text='Category of boundaries, e.g. "Community Areas".')
    singular = models.CharField(max_length=100,
        help_text='Name of a single boundary, e.g. "Community Area".')
    authority = models.CharField(max_length=256,
        help_text='The entity responsible for this data\'s accuracy, e.g. "City of Chicago".')
    domain = models.CharField(max_length=256,
        help_text='The area that this BoundarySet covers, e.g. "Chicago" or "Illinois".')
    last_updated = models.DateField(
        help_text='The last time this data was updated from its authority (but not necessarily the date it is current as of).')
    source_url = models.URLField(blank=True,
        help_text='The url this data was found at, if any.')
    notes = models.TextField(blank=True,
        help_text='Notes about loading this data, including any transformations that were applied to it.')
    licence_url = models.URLField(blank=True,
        help_text='The URL to the text of the licence this data is distributed under')

    class Meta:
        ordering = ('name',)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(BoundarySet, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    def as_dict(self):
        r = {
            'related': {
                'boundaries_url': urlresolvers.reverse('boundaryservice_boundary_list', kwargs={'set_slug': self.slug}),
            },
            'last_updated': unicode(self.last_updated),
        }
        for f in ('name', 'singular', 'authority', 'domain', 'source_url', 'notes'):
            r[f] = getattr(self, f)
        return r

    @staticmethod
    def get_dicts(sets):
        return [
            {
                'url': urlresolvers.reverse('boundaryservice_set_detail', kwargs={'slug': s.slug}),
                'related': {
                    'boundaries_url': urlresolvers.reverse('boundaryservice_boundary_list', kwargs={'set_slug': s.slug}),
                },
                'name': s.name,
                'domain': s.domain,
            } for s in sets
        ]

class Boundary(models.Model):
    """
    A boundary object, such as a Ward or Neighborhood.
    """
    set = models.ForeignKey(BoundarySet, related_name='boundaries',
        help_text='Category of boundaries that this boundary belongs, e.g. "Community Areas".')
    set_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, db_index=True)
    external_id = models.CharField(max_length=64,
        help_text='The boundaries\' unique id in the source dataset, or a generated one.')
    name = models.CharField(max_length=192, db_index=True,
        help_text='The name of this boundary, e.g. "Austin".')
    metadata = JSONField(blank=True,
        help_text='The complete contents of the attribute table for this boundary from the source shapefile, structured as json.')
    shape = models.MultiPolygonField(
        help_text='The geometry of this boundary in EPSG:4326 projection.')
    simple_shape = models.MultiPolygonField(
        help_text='The geometry of this boundary in EPSG:4326 projection and simplified to %s tolerance.' % app_settings.SIMPLE_SHAPE_TOLERANCE)
    centroid = models.PointField(
        null=True,
        help_text='The centroid (weighted center) of this boundary in EPSG:4326 projection.')
    
    objects = models.GeoManager()

    class Meta:
        unique_together = (('slug', 'set'))
        verbose_name_plural = 'Boundaries'

    def save(self, *args, **kwargs):
        return super(Boundary, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.set_name)

    @models.permalink
    def get_absolute_url(self):
        return 'boundaryservice_boundary_detail', [], {'set_slug': self.set_id, 'slug': self.slug}

    def as_dict(self):
        my_url = self.get_absolute_url()
        return {
            'related': {
                'boundary_set_url': urlresolvers.reverse('boundaryservice_set_detail', kwargs={'slug': self.set_id}),
                'shape_url': my_url + 'shape',
                'centroid_url': my_url + 'centroid',
                'simple_shape_url': my_url + 'simple_shape',
                'boundaries_url': urlresolvers.reverse('boundaryservice_boundary_list', kwargs={'set_slug': self.set_id}),
            },
            'boundary_set_name': self.set_name,
            'name': self.name,
            'metadata': self.metadata,
            'external_id': self.external_id,
        }

    @staticmethod
    def prepare_queryset_for_get_dicts(qs):
        return qs.values_list('slug', 'set', 'name', 'set_name')

    @staticmethod
    def get_dicts(boundaries):
        return [
            {
                'url': urlresolvers.reverse('boundaryservice_boundary_detail', kwargs={'slug': b[0], 'set_slug': b[1]}),
                'name': b[2],
                'related': {
                    'boundary_set_url': urlresolvers.reverse('boundaryservice_set_detail', kwargs={'slug': b[1]}),
                },
                'set_name': b[3],
            } for b in boundaries
        ]

